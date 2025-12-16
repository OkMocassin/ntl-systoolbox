# ntl-systoolbox
MSPR1 Ali

## Branch rules

- main:
  - protected
  - PR required
  - no direct push

- develop:
  - protected
  - PR required
  - integration branch

- feature/*:
  - created by developers
  - merged into develop via PR

⚠️ Architecture freeze:
Core structure, CLI entrypoint, config format and CheckResult contract are frozen.
Any change must be validated by P1.
