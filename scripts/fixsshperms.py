#!python3
import platform
import shutil
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent
DIST = BASE / "dist"
SSH_DIR = Path.home() / ".ssh"

def find_pwsh():
    for exe in ("pwsh", "powershell"):
        if shutil.which(exe):
            return exe
    raise RuntimeError("No PowerShell interpreter found")

def main():
    if not SSH_DIR.exists():
        print(f"~/.ssh does not exist at {SSH_DIR}")
        return

    system = platform.system().lower()

    if "windows" in system:
        print("Detected Windows → running fixperms.ps1")
        subprocess.run([find_pwsh(), str(DIST / "fixperms.ps1")], check=True)
    else:
        print("Detected Unix → running fixperms.sh")
        subprocess.run(["sh", str(DIST / "fixperms.sh")], check=True)

if __name__ == "__main__":
    main()
