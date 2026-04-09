import os
import copy
import yaml
from pathlib import Path

# Base project path
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Config locations
CONFIG_FILE = BASE_DIR / "config" / "config.yaml"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
LOG_DIR.mkdir(exist_ok=True)

# Default configuration settings (fallback if config.yaml is missing)
DEFAULT_CONFIG = {
    "app_name": "NTL System Toolbox",
    "version": "0.1.0",
    "theme": "default",
    "log_level": "INFO",
    "db": {
        "host": "localhost",
        "user": "root",
        "password_env": "DB_PASSWORD"
    },
    "backup_dir": BASE_DIR / "backups",
    "retention_days": 30
}

def _load_yaml_config() -> dict:
    """Load config from YAML file; return empty dict if missing or unreadable."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return yaml.safe_load(f) or {}
    except yaml.YAMLError:
        return {}

def _resolve_paths(config: dict) -> dict:
    """Convert a relative backup_dir string to an absolute Path."""
    backup_dir = config.get("backup_dir")
    if isinstance(backup_dir, str):
        path = Path(backup_dir)
        config["backup_dir"] = path if path.is_absolute() else BASE_DIR / path
    elif backup_dir is None:
        config["backup_dir"] = BASE_DIR / "backups"
    return config

def _apply_env_overrides(config: dict) -> dict:
    """Override selected config values with environment variables."""
    if os.environ.get("LOG_LEVEL"):
        config["log_level"] = os.environ["LOG_LEVEL"]
    if os.environ.get("DB_HOST"):
        config["db"]["host"] = os.environ["DB_HOST"]
    if os.environ.get("DB_USER"):
        config["db"]["user"] = os.environ["DB_USER"]
    return config

def _build_config() -> dict:
    config = copy.deepcopy(DEFAULT_CONFIG)
    yaml_config = _load_yaml_config()

    # Merge YAML values over defaults; deep-merge the nested 'db' block
    for key, value in yaml_config.items():
        if key == "db" and isinstance(value, dict):
            config["db"].update(value)
        else:
            config[key] = value

    _resolve_paths(config)
    _apply_env_overrides(config)
    return config

class Config:
    def __init__(self):
        self.config = _build_config()

    def get(self, key, default=None):
        return self.config.get(key, default)

settings = Config()
