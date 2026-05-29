import pathlib
import shutil
import subprocess
import sys


DEFAULT_REMOTE_URL = "git@github.com:guanyewu0900-cmyk/ClassPilot.git"


def run(command: list[str], cwd: pathlib.Path, dry_run: bool = False) -> int:
    print("+ " + " ".join(command))
    if dry_run:
        print("  dry-run: skipped")
        return 0
    return subprocess.run(command, cwd=cwd).returncode


def git_text(args: list[str], cwd: pathlib.Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def ensure_git(root: pathlib.Path) -> bool:
    if shutil.which("git") is None:
        print("Git was not found. Please install Git for Windows and make sure git is in PATH.", file=sys.stderr)
        return False
    if not (root / ".git").exists():
        print("This folder is not a Git repository yet. Run upload once first, or clone the GitHub repository.", file=sys.stderr)
        return False
    return True


def parse_download_args(args: list[str]) -> dict[str, str | bool]:
    options: dict[str, str | bool] = {
        "remote": "origin",
        "branch": "",
        "remote_url": "",
        "dry_run": False,
        "force": False,
        "rebase": False,
    }
    i = 0
    while i < len(args):
        arg = args[i]
        key = arg.lower()
        if key in ("--dry-run", "-dryrun"):
            options["dry_run"] = True
        elif key in ("--force", "-force"):
            options["force"] = True
        elif key in ("--rebase", "-rebase"):
            options["rebase"] = True
        elif key in ("--remote", "-remote"):
            i += 1
            if i >= len(args):
                raise ValueError(f"{arg} requires a value")
            options["remote"] = args[i]
        elif key in ("--branch", "-branch"):
            i += 1
            if i >= len(args):
                raise ValueError(f"{arg} requires a value")
            options["branch"] = args[i]
        elif key in ("--remote-url", "-remoteurl", "-remote_url"):
            i += 1
            if i >= len(args):
                raise ValueError(f"{arg} requires a value")
            options["remote_url"] = args[i]
        else:
            raise ValueError(f"Unknown download option: {arg}")
        i += 1
    return options


def download_latest(root: pathlib.Path, args: list[str]) -> int:
    try:
        options = parse_download_args(args)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        print_download_help()
        return 2

    if not ensure_git(root):
        return 1

    dry_run = bool(options["dry_run"])
    remote = str(options["remote"] or "origin")
    branch = str(options["branch"] or git_text(["branch", "--show-current"], root) or "main")
    remote_url = str(options["remote_url"] or "")

    if remote_url:
        current_url = git_text(["remote", "get-url", remote], root)
        if current_url:
            code = run(["git", "remote", "set-url", remote, remote_url], root, dry_run=dry_run)
        else:
            code = run(["git", "remote", "add", remote, remote_url], root, dry_run=dry_run)
        if code != 0:
            return code
    elif not git_text(["remote", "get-url", remote], root):
        code = run(["git", "remote", "add", remote, DEFAULT_REMOTE_URL], root, dry_run=dry_run)
        if code != 0:
            return code

    status = git_text(["status", "--porcelain"], root)
    if status and not options["force"]:
        print("Local files have uncommitted changes. Commit/upload them first, or rerun with download --force.")
        print("Changed files:")
        for line in status.splitlines():
            print(f"  {line}")
        if not dry_run:
            return 1
        print("  dry-run: a real download would stop here.")

    fetch_code = run(["git", "fetch", remote, branch], root, dry_run=dry_run)
    if fetch_code != 0:
        return fetch_code

    if options["rebase"]:
        update_args = ["git", "pull", "--rebase", remote, branch]
    else:
        update_args = ["git", "pull", "--ff-only", remote, branch]

    update_code = run(update_args, root, dry_run=dry_run)
    if update_code != 0:
        print("Download did not finish cleanly. If your local branch has commits that GitHub does not have, try: python push_to_git.py download --rebase", file=sys.stderr)
        return update_code

    if dry_run:
        print("Dry run complete. No local files were changed.")
    else:
        print("Done. Your local code has been updated from GitHub.")
    return 0


def print_download_help() -> None:
    print(
        "Usage:\n"
        "  python push_to_git.py                 # upload/push, same as before\n"
        "  python push_to_git.py upload -Message \"Update website\"\n"
        "  python push_to_git.py download        # download latest from origin/current-branch\n"
        "  python push_to_git.py pull --branch main --rebase\n\n"
        "Download options:\n"
        "  --remote origin        Git remote name, default origin\n"
        "  --branch main          Branch to download, default current branch or main\n"
        "  --remote-url URL       Set/add the remote URL before downloading\n"
        "  --rebase               Rebase local commits on top of GitHub latest\n"
        "  --force                Allow downloading even with uncommitted local changes\n"
        "  --dry-run              Show commands without running them"
    )


def upload(root: pathlib.Path, args: list[str]) -> int:
    script = root / "sync-github.ps1"
    if not script.exists():
        print(f"Upload script was not found: {script}", file=sys.stderr)
        return 1

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
        *args,
    ]

    result = subprocess.run(command, cwd=root)
    return result.returncode


def main() -> int:
    root = pathlib.Path(__file__).resolve().parent
    args = sys.argv[1:]
    if args and args[0].lower() in ("download", "pull", "sync-down"):
        return download_latest(root, args[1:])
    if args and args[0].lower() in ("help", "--help", "-h"):
        print_download_help()
        return 0
    if args and args[0].lower() in ("upload", "push", "sync-up"):
        return upload(root, args[1:])
    return upload(root, args)


if __name__ == "__main__":
    raise SystemExit(main())
