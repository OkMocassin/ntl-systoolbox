import shutil
import psutil
import subprocess
import yaml
import os
from pathlib import Path
from typing import List
import mysql.connector
from ntlsystoolbox.core.models import CheckResult, Status
from ntlsystoolbox.core.config import settings, BASE_DIR
from ntlsystoolbox.core.logging_conf import logger

REMEDIATION_FILE = BASE_DIR / "config" / "remediation_catalog.yaml"

def load_remediation_catalog():
    if not REMEDIATION_FILE.exists():
        return {}
    with open(REMEDIATION_FILE, "r") as f:
        return yaml.safe_load(f) or {}

CATALOG = load_remediation_catalog()

def attach_remediation(result: CheckResult, key: str):
    """Injects recommendation and runbook link if a check fails."""
    if result.status != Status.OK and "checks" in CATALOG:
        entry = CATALOG["checks"].get(key)
        if entry:
            result.recommendation = f"{entry.get('recommendation')} (See {entry.get('runbook')})"

def check_ad_services() -> List[CheckResult]:
    results = []
    # List of critical services to check (Windows)
    services = ["Dnscache", "LanmanServer", "Netlogon"] 
    # Note: "ADWS" (Active Directory Web Services) usually only on Domain Controllers. 
    # We stick to generic ones for this local test unless specified.
    
    for svc in services:
        try:
            # sc query <service>
            cmd = subprocess.run(["sc", "query", svc], capture_output=True, text=True)
            if "RUNNING" in cmd.stdout:
                results.append(CheckResult(f"Service: {svc}", Status.OK, "Running"))
            else:
                res = CheckResult(f"Service: {svc}", Status.CRITICAL, "Not Running or Not Found")
                attach_remediation(res, "ad_service_failure")
                results.append(res)
        except FileNotFoundError:
             # Non-windows or sc not found
             results.append(CheckResult(f"Service: {svc}", Status.UNKNOWN, "'sc' command not found (Not on Windows?)"))
    return results

def check_mysql_health() -> List[CheckResult]:
    results = []
    db_config = settings.get("db")
    
    # Try to connect
    try:
        # In a real scenario, use actual credentials. Here we mock or allow failure.
        # Passwords should come from env vars in a real app.
        conn = mysql.connector.connect(
            host=db_config.get("host"),
            user=db_config.get("user"),
            password=os.environ.get(db_config.get("password_env"), ""),
            connection_timeout=2
        )
        if conn.is_connected():
            results.append(CheckResult("MySQL Connectivity", Status.OK, "Connected successfully"))
            conn.close()
    except mysql.connector.Error as err:
        res = CheckResult("MySQL Connectivity", Status.CRITICAL, f"Connection failed: {err}")
        attach_remediation(res, "mysql_connection_error")
        results.append(res)
    except Exception as e:
         results.append(CheckResult("MySQL Connectivity", Status.CRITICAL, f"Unexpected error: {e}"))
         
    return results

def check_os_metrics() -> List[CheckResult]:
    results = []
    
    # Disk
    fw = psutil.disk_usage("/")
    if fw.percent > 90:
        res = CheckResult("Disk Usage", Status.CRITICAL, f"{fw.percent}% used")
        attach_remediation(res, "os_disk_critical")
        results.append(res)
    elif fw.percent > 80:
         results.append(CheckResult("Disk Usage", Status.WARNING, f"{fw.percent}% used"))
    else:
         results.append(CheckResult("Disk Usage", Status.OK, f"{fw.percent}% used"))

    # Memory
    mem = psutil.virtual_memory()
    if mem.percent > 90:
        res = CheckResult("Memory Usage", Status.CRITICAL, f"{mem.percent}% used")
        attach_remediation(res, "os_ram_critical")
        results.append(res)
    else:
        results.append(CheckResult("Memory Usage", Status.OK, f"{mem.percent}% used"))

    # CPU
    cpu = psutil.cpu_percent(interval=1)
    if cpu > 90:
         results.append(CheckResult("CPU Usage", Status.WARNING, f"{cpu}% load"))
    else:
         results.append(CheckResult("CPU Usage", Status.OK, f"{cpu}% load"))

    return results

def run_diagnostic() -> List[CheckResult]:
    logger.info("Starting full diagnostic scan...")
    all_results = []
    
    all_results.extend(check_os_metrics())
    all_results.extend(check_ad_services())
    all_results.extend(check_mysql_health())
    
    return all_results
