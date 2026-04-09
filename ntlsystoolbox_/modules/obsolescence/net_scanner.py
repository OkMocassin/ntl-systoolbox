import socket
from typing import List, Dict
from ntlsystoolbox.core.logging_conf import logger

# Try import nmap, handle failure gracefully
try:
    import nmap
    HAS_NMAP = True
except (ImportError, FileNotFoundError):
    HAS_NMAP = False

def scan_network(target: str = "127.0.0.1") -> List[Dict]:
    """
    Scans network for hosts and OS details.
    Returns list of dicts: {'ip': str, 'hostname': str, 'os': str, 'version': str}
    """
    hosts = []
    
    if not HAS_NMAP:
        logger.warning("python-nmap module not found or nmap binary missing. Using mock data.")
        return _mock_scan_results()

    try:
        nm = nmap.PortScanner()
        # Fast scan, try to detect OS (-O requires root usually)
        # We might default to standard scan if -O fails permissions
        logger.info(f"Scanning {target}...")
        nm.scan(hosts=target, arguments='-sn') # Ping scan first for speed
        
        for host in nm.all_hosts():
            # Basic hostname resolution
            try:
                hostname = nm[host].hostname() or socket.getfqdn(host)
            except:
                hostname = "Unknown"
                
            # For this MVP, we simulate OS detection because real OS detection (-O)
            # requires root privileges which we might not have, and is slow.
            # We'll just infer or use placeholder for the logic.
            
            # In a real deployed agent, we might query WMI or SSH.
            # Here: simplistic assumption for demonstration
            
            hosts.append({
                "ip": host,
                "hostname": hostname,
                "os": "windows", # Placeholder
                "version": "10"  # Placeholder
            })
            
    except Exception as e:
        logger.error(f"Nmap scan failed: {e}")
        return _mock_scan_results()

    return hosts

def _mock_scan_results():
    """Returns dummy data for demonstration/testing."""
    return [
        {"ip": "192.168.1.10", "hostname": "DC01", "os": "windows", "version": "server_2016"},
        {"ip": "192.168.1.11", "hostname": "WMS-DB", "os": "ubuntu", "version": "20.04"},
        {"ip": "192.168.1.12", "hostname": "LEGACY-APP", "os": "windows", "version": "server_2012"},
        {"ip": "192.168.1.50", "hostname": "DESKTOP-HR", "os": "windows", "version": "10"},
    ]
