import sys
from rich.table import Table
from rich.console import Console
from ntlsystoolbox.core.config import settings
from ntlsystoolbox.core.logging_conf import logger
from ntlsystoolbox.core import io_utils
from ntlsystoolbox.core.models import Status
from ntlsystoolbox.modules.diagnostic import run_diagnostic

console = Console()

def display_results(results):
    """
    Renders diagnostic, backup, or obsolescence check results in a formatted Rich table.

    Args:
        results (List[CheckResult]): A list of result objects to display. Each object
                                     should contain check_name, status, message, and recommendation.
    """
    table = Table(title="Diagnostic Results")
    table.add_column("Check", style="cyan", no_wrap=True)
    table.add_column("Status", justify="center")
    table.add_column("Message", style="magenta")
    table.add_column("Recommendation", style="green")

    for res in results:
        status_style = "green" if res.status.name == "OK" else "red bold" if res.status.name == "CRITICAL" else "yellow"
        table.add_row(
            res.check_name,
            f"[{status_style}]{res.status.value}[/{status_style}]",
            res.message,
            res.recommendation or ""
        )
    
    console.print(table)
    io_utils.print_info(f"Total checks: {len(results)}")

def _worst_exit_code(results) -> int:
    """Return 0 (all OK), 1 (any WARNING), or 2 (any CRITICAL)."""
    code = 0
    for res in results:
        if res.status == Status.CRITICAL:
            return 2
        if res.status == Status.WARNING:
            code = 1
    return code

def main_menu():
    """
    Displays the interactive main menu using Questionary.
    Allows the user to select and run the different toolbox modules.
    """
    while True:
        io_utils.print_header(f"{settings.get('app_name')} v{settings.get('version')}", "Main Menu")
        
        choice = io_utils.select_option(
            "Select a module:",
            choices=[
                "Diagnostic Module (Check Health)",
                "Backup Module (MySQL Backup)",
                "Obsolescence Module (EOL Audit)",
                "Exit"
            ]
        )
        
        if choice == "Exit":
            io_utils.print_info("Exiting...")
            sys.exit(0)
        elif choice.startswith("Diagnostic"):
            try:
                io_utils.print_info("Running diagnostics...")
                results = run_diagnostic()
                display_results(results)
                io_utils.wait_for_enter()
            except Exception as e:
                logger.exception("Diagnostic failed")
                io_utils.print_error(f"Error running diagnostics: {e}")
                io_utils.wait_for_enter()
        elif choice.startswith("Backup"):
            action = io_utils.select_option("Backup Module Actions:", [
                "Full Backup (Dry Run)",
                "Full Backup (Execute)",
                "Export Table to CSV",
                "Cleanup Old Backups",
                "Back to Main Menu"
            ])
            
            from ntlsystoolbox.modules.backup import run_full_backup, export_table_to_csv, cleanup_old_backups
            
            if action == "Full Backup (Dry Run)":
                res = run_full_backup(dry_run=True)
                display_results([res])
            elif action == "Full Backup (Execute)":
                if io_utils.confirm_action("Start full database backup?"):
                    res = run_full_backup(dry_run=False)
                    display_results([res])
            elif action == "Export Table to CSV":
                # For now just asking for table name, ideally we list tables
                import questionary
                table = questionary.text("Enter table name:").ask()
                if table:
                    res = export_table_to_csv(table)
                    display_results([res])
            elif action == "Cleanup Old Backups":
                if io_utils.confirm_action("Delete old backups?"):
                    res = cleanup_old_backups()
                    display_results([res])
            
            io_utils.wait_for_enter()
        elif choice.startswith("Obsolescence"):
            io_utils.print_info("Starting Network Scan & EOL Audit...")
            from ntlsystoolbox.modules.obsolescence import run_obsolescence_audit
            
            # Ask for target subnet or use default
            target = io_utils.select_option("Select Scan Target:", ["Default (Mock/Local)", "Custom IP/Subnet"])
            subnet = "192.168.1.0/24"
            if target == "Custom IP/Subnet":
                 import questionary
                 subnet = questionary.text("Enter target (e.g. 10.0.0.0/24):").ask()
            
            results = run_obsolescence_audit(subnet)
            display_results(results)
            io_utils.wait_for_enter()
            
def main():
    """
    Entry point for the NTL System Toolbox CLI application.
    Parses command-line arguments to either run specific modules directly
    or launch the interactive `main_menu`.
    """
    import argparse
    parser = argparse.ArgumentParser(description="NTL System Toolbox")
    parser.add_argument("--module", choices=["diagnostic", "backup", "obsolescence"], help="Module to run")
    parser.add_argument("--action", help="Action to perform within the module")
    parser.add_argument("--target", help="Target IP/Subnet for EOL audit")
    args = parser.parse_args()

    try:
        logger.info("Starting application...")
        
        if args.module:
            results = []
            if args.module == "diagnostic":
                from ntlsystoolbox.modules.diagnostic import run_diagnostic
                results = run_diagnostic()
                display_results(results)
            elif args.module == "backup":
                from ntlsystoolbox.modules.backup import run_full_backup, export_table_to_csv, cleanup_old_backups
                if args.action == "dry-run":
                    res = run_full_backup(dry_run=True)
                    display_results([res])
                    results = [res]
                elif args.action == "full":
                    res = run_full_backup(dry_run=False)
                    display_results([res])
                    results = [res]
                elif args.action == "export":
                    io_utils.print_warning("Export via CLI args not fully implemented yet.")
                elif args.action == "cleanup":
                    res = cleanup_old_backups()
                    display_results([res])
                    results = [res]
                else:
                    io_utils.print_error(f"Unknown action: {args.action}")
            elif args.module == "obsolescence":
                from ntlsystoolbox.modules.obsolescence import run_obsolescence_audit
                target = args.target or "192.168.1.0/24"
                results = run_obsolescence_audit(target)
                display_results(results)
            sys.exit(_worst_exit_code(results))
        else:
            main_menu()
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user.")
        sys.exit(0)
    except Exception as e:
        logger.exception("An unexpected error occurred.")
        io_utils.print_error(f"Critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
