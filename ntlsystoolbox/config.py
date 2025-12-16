import os
import yaml

def load_config(path="config.yaml"):
    with open(path, "r") as f:
        config = yaml.safe_load(f)

    mysql = config.get("mysql")
    if mysql:
        env_key = mysql.get("password_env")
        if env_key:
            mysql["password"] = os.getenv(env_key)

    return config
