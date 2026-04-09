import os
import subprocess
import csv
import time
from datetime import datetime, timedelta
from pathlib import Path
import mysql.connector
from ntlsystoolbox.core.config import settings
from ntlsystoolbox.core.logging_conf import logger
from ntlsystoolbox.core.models import CheckResult, Status
from ntlsystoolbox.modules.diagnostic.diagnostic_checks import attach_remediation

def get_backup_path() -> Path:
    path = settings.get("backup_dir")
    if isinstance(path, str):
        path = Path(path)
    path.mkdir(exist_ok=True)
    return path

def run_full_backup(dry_run: bool = False) -> CheckResult:
    """Executes mysqldump to backup the database."""
    db_config = settings.get("db")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"backup_{timestamp}.sql"
    output_path = get_backup_path() / filename
    
    # Construct command
    # Using subprocess with shell=True or passing args list.
    # Warning: Putting password in args list is visible in process list.
    # Better to use config file for mysqldump, but for this scope we might pass it via env or command line.
    
    password = os.environ.get(db_config.get("password_env"), "")
    
    # mysqldump -u <user> -p<password> -h <host> --all-databases > output.sql
    # Note: No space after -p
    cmd = [
        "mysqldump",
        f"-u{db_config.get('user')}",
        f"-h{db_config.get('host')}",
        "--all-databases",
        f"--result-file={output_path}"
    ]
    
    # Create a safe display string masking password if we were passing it explicitly,
    # but here -p is concatenated. Ideally we use defaults-extra-file.
    
    # Inject password into env for command execution to avoid showing in process list if possible,
    # but mysqldump typically reads from file or -p argument. 
    # Let's use the password environment variable approach if supported by mysqldump (MYSQL_PWD).
    
    env = os.environ.copy()
    if password:
        env["MYSQL_PWD"] = password
    
    if dry_run:
        logger.info(f"[Dry Run] would execute: {' '.join(cmd)}")
        return CheckResult("Backup (Dry Run)", Status.OK, f"Would create {filename}")
    
    try:
        start_time = time.time()
        logger.info(f"Starting backup to {output_path}...")
        
        # We don't pass password in args to subprocess if we use MYSQL_PWD, 
        # but we need to remove the '-p' flag then. 
        # Actually mysqldump command line needs -p if not using env, but MYSQL_PWD env var is standard libmysqlclient.
        
        result = subprocess.run(
            cmd, 
            env=env, 
            check=True, 
            capture_output=True, 
            text=True
        )
        
        duration = time.time() - start_time
        size_mb = output_path.stat().st_size / (1024 * 1024)
        
        return CheckResult(
            "Full Backup", 
            Status.OK, 
            f"Success: {filename} ({size_mb:.2f} MB) in {duration:.2f}s"
        )
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Backup failed: {e.stderr}")
        res = CheckResult("Full Backup", Status.CRITICAL, f"mysqldump failed with code {e.returncode}")
        attach_remediation(res, "backup_mysql_mysqldump_failed")
        return res
    except FileNotFoundError:
        res = CheckResult("Full Backup", Status.CRITICAL, "mysqldump command not found in PATH")
        attach_remediation(res, "backup_mysql_mysqldump_failed")
        return res
    except Exception as e:
        logger.exception("Backup error")
        return CheckResult("Full Backup", Status.CRITICAL, f"Unexpected error: {str(e)}")

def export_table_to_csv(table_name: str) -> CheckResult:
    """Exports a specific table to CSV."""
    db_config = settings.get("db")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"export_{table_name}_{timestamp}.csv"
    output_path = get_backup_path() / filename
    
    try:
        conn = mysql.connector.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=os.environ.get(db_config.get("password_env"), "")
        )
        
        cursor = conn.cursor()
        
        # Check if table exists (basic injection check roughly, though internal tool)
        cursor.execute("SHOW TABLES LIKE %s", (table_name,))
        if not cursor.fetchone():
            return CheckResult("Export Table", Status.CRITICAL, f"Table '{table_name}' not found")
            
        query = f"SELECT * FROM `{table_name}`"
        cursor.execute(query)
        
        rows = cursor.fetchall()
        column_names = [i[0] for i in cursor.description]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(column_names)
            writer.writerows(rows)
            
        conn.close()
        return CheckResult("Export Table", Status.OK, f"Exported {len(rows)} rows to {filename}")

    except mysql.connector.Error as e:
        res = CheckResult("Export Table", Status.CRITICAL, f"DB Error: {e}")
        attach_remediation(res, "backup_mysql_connection_error")
        return res
    except Exception as e:
        return CheckResult("Export Table", Status.CRITICAL, f"Error: {e}")

def cleanup_old_backups() -> CheckResult:
    """Removes backups older than retention_days."""
    days = settings.get("retention_days", 30)
    cutoff = datetime.now() - timedelta(days=days)
    backup_dir = get_backup_path()
    
    deleted_count = 0
    errors = 0
    
    try:
        for file_path in backup_dir.glob("backup_*.sql"):
            # Check modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if mtime < cutoff:
                try:
                    file_path.unlink()
                    deleted_count += 1
                    logger.info(f"Deleted old backup: {file_path.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")
                    errors += 1
        
        msg = f"Cleaned {deleted_count} files older than {days} days."
        if errors > 0:
            return CheckResult("Cleanup Backups", Status.WARNING, f"{msg} ({errors} errors)")
        return CheckResult("Cleanup Backups", Status.OK, msg)
        
    except Exception as e:
        return CheckResult("Cleanup Backups", Status.CRITICAL, f"Cleanup failed: {e}")
