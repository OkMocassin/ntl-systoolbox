from typing import List
import csv
from datetime import datetime
from ntlsystoolbox.core.config import settings
from ntlsystoolbox.core.models import CheckResult, Status
from ntlsystoolbox.core.logging_conf import logger
from ntlsystoolbox.modules.diagnostic.diagnostic_checks import attach_remediation
from .eol_db import get_eol_status
from .net_scanner import scan_network

def run_obsolescence_audit(target_subnet: str = "192.168.1.0/24") -> List[CheckResult]:
    logger.info(f"Starting EOL Audit on {target_subnet}...")
    
    hosts = scan_network(target_subnet)
    results = []
    
    # Process findings
    host_summary = []
    
    for host in hosts:
        ip = host.get('ip')
        name = host.get('hostname')
        os_fam = host.get('os')
        ver = host.get('version')
        
        status, msg, eol_date = get_eol_status(os_fam, ver)
        
        check_name = f"Host {name} ({ip})"
        detail_msg = f"{os_fam} {ver}: {msg}"
        
        res = CheckResult(check_name, status, detail_msg)
        
        if status == Status.CRITICAL:
            attach_remediation(res, "eol_os_unsupported")
        elif status == Status.WARNING:
            attach_remediation(res, "eol_os_near_eol")
            
        results.append(res)
        
        host_summary.append({
            "ip": ip,
            "hostname": name,
            "os": os_fam,
            "version": ver,
            "status": status.value,
            "eol_date": eol_date
        })
        
    # Auto-export report
    export_report(host_summary)
    
    return results

def export_report(data: List[dict]):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = settings.get("backup_dir") / f"eol_audit_{timestamp}.csv" # Reuse backup dir for reports or specific report dir
    path.parent.mkdir(exist_ok=True)
    
    if not data:
        return

    try:
        keys = data[0].keys()
        with open(path, 'w', newline='') as f:
            dict_writer = csv.DictWriter(f, keys)
            dict_writer.writeheader()
            dict_writer.writerows(data)
        logger.info(f"Audit report saved to {path}")
    except Exception as e:
        logger.error(f"Failed to export audit report: {e}")
