from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Any

class Status(Enum):
    OK = "OK"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"

@dataclass
class CheckResult:
    check_name: str
    status: Status
    message: str
    details: Optional[Any] = None
    recommendation: Optional[str] = None
    
    def __str__(self):
        return f"[{self.status.value}] {self.check_name}: {self.message}"
