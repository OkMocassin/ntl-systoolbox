import yaml
from datetime import datetime
from typing import Tuple, Optional
from ntlsystoolbox.core.config import BASE_DIR
from ntlsystoolbox.core.models import Status

EOL_DB_FILE = BASE_DIR / "config" / "eol_os_db.yaml"

def load_eol_db():
    if not EOL_DB_FILE.exists():
        return {}
    with open(EOL_DB_FILE, "r") as f:
        return yaml.safe_load(f) or {}

EOL_DB = load_eol_db()

def get_eol_status(os_family: str, version: str) -> Tuple[Status, str, str]:
    """
    Returns (Status, Message, EOL_Date_String).
    """
    os_family = os_family.lower()
    version = str(version)
    
    if os_family not in EOL_DB.get("os_lifecycle", {}):
        return Status.UNKNOWN, "OS Family not found in DB", "N/A"
    
    versions = EOL_DB["os_lifecycle"][os_family]
    if version not in versions:
         return Status.UNKNOWN, f"Version {version} not found for {os_family}", "N/A"
         
    eol_str = versions[version]
    try:
        eol_date = datetime.strptime(eol_str, "%Y-%m-%d")
        now = datetime.now()
        
        if now > eol_date:
            return Status.CRITICAL, f"EOL passed on {eol_str}", eol_str
        elif (eol_date - now).days < 365:
            return Status.WARNING, f"EOL approaching ({eol_str})", eol_str
        else:
            return Status.OK, f"Supported until {eol_str}", eol_str
            
    except ValueError:
        return Status.UNKNOWN, f"Invalid date format in DB: {eol_str}", eol_str
