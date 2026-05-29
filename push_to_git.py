import pathlib
import shutil
import subprocess
import sys


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent
    script = root / "sync-github.ps1"
    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if powershell is None:
        print("PowerShell was not found. Please install PowerShell or run this script on Windows.", file=sys.stderr)
        return 1

    command = [
        powershell,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(script),
        *sys.argv[1:],
    ]

    result = subprocess.run(command, cwd=root)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
