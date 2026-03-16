"""
System Integration - Yibo
=========================
Auto-launch and OS integration utilities.
"""

import platform
import os
from pathlib import Path


def get_auto_launch_script_path():
    """Return the appropriate auto-launch script path for the current OS."""
    base = Path(__file__).parent
    system = platform.system()
    if system == "Windows":
        return base / "auto_launch_windows.bat"
    else:
        return base / "auto_launch_mac.sh"


def enable_auto_launch():
    """
    Windows: Copy .bat to shell:startup folder.
    Mac/Linux: Print instructions for adding to login items or crontab.

    Returns a status message string.
    """
    system = platform.system()
    script = get_auto_launch_script_path()

    if not script.exists():
        return f"Auto-launch script not found at {script}"

    if system == "Windows":
        startup_folder = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        if startup_folder.exists():
            import shutil
            dest = startup_folder / script.name
            shutil.copy2(str(script), str(dest))
            return f"Auto-launch enabled. Script copied to {dest}"
        else:
            return f"Could not find Windows Startup folder. Manually copy {script} to your Startup folder."
    elif system == "Darwin":
        return (
            f"To enable auto-launch on macOS:\n"
            f"1. Open System Preferences > Users & Groups > Login Items\n"
            f"2. Add Terminal or iTerm\n"
            f"3. Create a login script that runs: bash {script}\n"
            f"Or add to crontab: @reboot bash {script}"
        )
    else:
        return (
            f"To enable auto-launch on Linux:\n"
            f"Add to your crontab: @reboot bash {script}\n"
            f"Or add to ~/.bashrc: bash {script}"
        )


def disable_auto_launch():
    """
    Remove the startup entry.

    Returns a status message string.
    """
    system = platform.system()

    if system == "Windows":
        startup_folder = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        bat_file = startup_folder / "auto_launch_windows.bat"
        if bat_file.exists():
            bat_file.unlink()
            return "Auto-launch disabled. Removed from Windows Startup."
        else:
            return "Auto-launch was not enabled (no script in Startup folder)."
    else:
        return (
            "To disable auto-launch:\n"
            "Remove the sleep tracker entry from your crontab (crontab -e)\n"
            "or remove it from Login Items in System Preferences."
        )
