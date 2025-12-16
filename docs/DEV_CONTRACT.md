## CheckResult contract

Every module must return a dict with:

- check_id (string)
- target (string)
- status: OK | WARNING | CRITICAL
- message (string)
- details (dict)

Optional:
- recommendation (dict)
