import logging
from rich.logging import RichHandler
from ntlsystoolbox.core.config import settings

def setup_logging():
    log_level = settings.get("log_level", "INFO")
    
    logging.basicConfig(
        level=log_level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)]
    )
    
    # Silence third-party libs
    logging.getLogger("mysql.connector").setLevel(logging.WARNING)

    return logging.getLogger("ntlsystoolbox")

logger = setup_logging()
