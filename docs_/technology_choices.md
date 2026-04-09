# NTL System Toolbox: Technology Choices & Architecture

This document outlines the core technologies used to build the NTL System Toolbox, the alternatives that were considered, and the reasoning behind the final architectural choices.

## 1. Core Language: Python
The entire application is written in Python (3.9+). 

* **Alternatives Considered:** 
  * *Go (Golang):* Excellent for CLI tools and compiles to a single binary, but has a steeper learning curve for quick automation scripts.
  * *Bash / PowerShell:* Native to OS, but extremely difficult to scale, test, and build complex interactive UIs with.
  * *Node.js:* Good ecosystem, but less idiomatic for low-level system administration compared to Python.
* **Why we chose Python:** Python is the undisputed king of IT automation and scripting. It has a massive ecosystem of system administration libraries (like `psutil`), is highly readable, and allows for rapid feature iteration.

## 2. Interactive UI: Rich & Questionary
To handle terminal output and user input, we combined two powerful UI libraries.

* **Alternatives Considered:**
  * *Standard `argparse` / `Click` / `Typer`:* Traditional flag-based CLIs (`tool --run-diag --target 10.0.0.1`). 
  * *Curses / Textual:* Full-screen terminal interfaces.
* **Why we chose Rich & Questionary:** Traditional CLIs force users to memorize long lists of flags, which can cause costly mistakes in production. `Questionary` provides an interactive, guided menu system (arrow-key navigation), reducing human error. `Rich` renders gorgeous tables, colors, and progress bars, making log output instantly readable and highlighting critical failures in bold red.

## 3. System Diagnostics: `psutil`
Used for querying the operating system for CPU, RAM, and disk utilization.

* **Alternatives Considered:**
  * *OS-specific commands (`wmic`, `top`, `df`):* Parsing shell output manually.
  * *Built-in `os` / `sys` modules:* Very limited in scope.
* **Why we chose `psutil`:** It provides a clean, cross-platform API. We don't need to write custom parsers for Windows vs Linux to get RAM usage; `psutil` handles that abstraction flawlessly.

## 4. Database Management: `mysql-connector-python`
Handles connections for the Backup module.

* **Alternatives Considered:**
  * *SQLAlchemy:* A massive ORM.
  * *PyMySQL:* A pure Python MySQL client.
* **Why we chose `mysql-connector-python`:** It is the official Oracle-supported driver for MySQL. Because the toolbox runs administrative tasks (like triggering `mysqldump` and schema checks) rather than complex application queries, a lightweight driver was preferred over a heavy ORM like SQLAlchemy.

## 5. Network Discovery: `python-nmap`
Powers the Obsolescence module by scanning subnets for active devices.

* **Alternatives Considered:**
  * *Scapy:* A powerful packet manipulation program.
  * *Native Python `socket`:* Writing a custom ping-sweeper.
* **Why we chose `python-nmap`:** Building a custom port scanner is reinventing the wheel and often triggers false positives or misses hosts. Nmap is the industry standard for network discovery. `python-nmap` simply acts as a wrapper, leveraging Nmap's decades of reliable scanning logic and parsing its output into usable Python dictionaries.

## 6. Data Validation & Config: `pydantic` & `PyYAML`
Used for loading configurations and ensuring data schemas (like `CheckResult`) are strictly typed.

* **Alternatives Considered:**
  * *Python `dataclasses` & `json`:* Built into standard library.
* **Why we chose Pydantic & PyYAML:** Sysadmins prefer YAML over JSON for configuration files because it supports comments and is visually cleaner. Pydantic guarantees that the data flowing through the app (especially after parsing unpredictable shell command outputs) matches explicitly defined schemas, preventing runtime crashes.
