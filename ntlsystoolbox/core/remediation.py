import yaml

def load_catalog(path="ntlsystoolbox/data/remediation_catalog.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}

def attach_recommendation(check_result, catalog):
    key = check_result.get("check_id")
    status = check_result.get("status")

    entry = catalog.get(key, {}).get(status)
    if entry:
        check_result["recommendation"] = entry

    return check_result
