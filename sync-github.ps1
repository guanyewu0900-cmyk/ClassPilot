param(
  [string]$Message = "Update website",
  [string]$RemoteUrl = "",
  [switch]$SkipCommit,
  [switch]$NoPull,
  [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
if ([string]::IsNullOrWhiteSpace($RemoteUrl)) {
  if (-not [string]::IsNullOrWhiteSpace($env:CLASSPILOT_REMOTE_URL)) {
    $RemoteUrl = $env:CLASSPILOT_REMOTE_URL
  } else {
    $RemoteUrl = "https://github.com/guanyewu0900-cmyk/classpilot.git"
  }
}
$SafeRoot = $Root -replace "\\", "/"

function Run-Git {
  param([string[]]$GitArgs)
  Write-Host "+ git $($GitArgs -join ' ')" -ForegroundColor Cyan
  if ($DryRun) {
    Write-Host "  dry-run: skipped" -ForegroundColor DarkGray
    return
  }
  & git @GitArgs
  if ($LASTEXITCODE -ne 0) {
    throw "git $($GitArgs -join ' ') failed with exit code $LASTEXITCODE"
  }
}

function Get-GitText {
  param([string[]]$GitArgs)
  $oldErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    $output = (& git @GitArgs 2>$null)
    $code = $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
  if ($code -ne 0) {
    return ""
  }
  return ($output -join "`n").Trim()
}

function Get-GitExitCode {
  param([string[]]$GitArgs)
  $oldErrorActionPreference = $ErrorActionPreference
  $ErrorActionPreference = "Continue"
  try {
    & git @GitArgs *> $null
    return $LASTEXITCODE
  } finally {
    $ErrorActionPreference = $oldErrorActionPreference
  }
}

function Ensure-GitIdentity {
  $name = Get-GitText @("config", "user.name")
  $email = Get-GitText @("config", "user.email")
  if ([string]::IsNullOrWhiteSpace($name) -or [string]::IsNullOrWhiteSpace($email)) {
    throw "Git user.name and user.email are required before committing. Run: git config --global user.name `"Your Name`"; git config --global user.email `"you@example.com`""
  }
}

Set-Location $Root

& git --version *> $null
if ($LASTEXITCODE -ne 0) {
  throw "Git was not found. Please install Git for Windows and make sure git is in PATH."
}

if ($DryRun) {
  Write-Host "Dry run for ClassPilot Git sync" -ForegroundColor Green
  Write-Host "Root: $Root"
  Write-Host "Remote: $RemoteUrl"
  if (-not (Test-Path ".git")) {
    Write-Host "Repository is not initialized yet. A normal run will create .git and set branch main."
  } else {
    $branchPreview = Get-GitText @("branch", "--show-current")
    if ([string]::IsNullOrWhiteSpace($branchPreview)) { $branchPreview = "main" }
    $originPreview = Get-GitText @("remote", "get-url", "origin")
    $statusPreview = Get-GitText @("status", "--porcelain")
    Write-Host "Branch: $branchPreview"
    if ($originPreview) { Write-Host "Current origin: $originPreview" } else { Write-Host "Current origin: none" }
    if ($statusPreview) { Write-Host "Working tree has changes that would be committed." } else { Write-Host "Working tree is clean." }
  }
  Write-Host "No files, commits, remotes, pulls, or pushes were changed."
  exit 0
}

if (-not (Test-Path ".git")) {
  Run-Git @("init")
  Run-Git @("branch", "-M", "main")
}

Write-Host "+ git config --global --add safe.directory $SafeRoot" -ForegroundColor Cyan
& git config --global --add safe.directory $SafeRoot
if ($LASTEXITCODE -ne 0) {
  Write-Host "Warning: could not update global safe.directory. Continuing because this repository is already accessible." -ForegroundColor Yellow
}

$branch = (& git branch --show-current).Trim()
if (-not $branch) {
  Run-Git @("branch", "-M", "main")
  $branch = "main"
}
Write-Host "Branch: $branch"

$origin = Get-GitText @("remote", "get-url", "origin")
if (-not $origin) {
  Run-Git @("remote", "add", "origin", $RemoteUrl)
} elseif ($origin.Trim() -ne $RemoteUrl) {
  Write-Host "Updating origin from $($origin.Trim()) to $RemoteUrl"
  Run-Git @("remote", "set-url", "origin", $RemoteUrl)
} else {
  Write-Host "Origin: $RemoteUrl"
}

if (-not $SkipCommit) {
  $status = (& git status --porcelain)
  if ($status) {
    Ensure-GitIdentity
    Run-Git @("add", "-A")
    $staged = (& git diff --cached --name-only)
    if ($staged) {
      Run-Git @("commit", "-m", $Message)
    } else {
      Write-Host "No staged changes to commit."
    }
  } else {
    Write-Host "Working tree is clean. Nothing to commit."
  }
}

if (-not $NoPull) {
  Write-Host "Checking remote branch before push..."
  $remoteCheck = Get-GitExitCode @("ls-remote", "--exit-code", "--heads", "origin", $branch)
  if ($remoteCheck -eq 0) {
    Run-Git @("pull", "--rebase", "origin", $branch)
  } elseif ($remoteCheck -eq 2) {
    Write-Host "Remote branch origin/$branch does not exist yet. Skipping pull."
  } else {
    throw "Could not check origin/$branch. Please verify your GitHub login, network, or proxy settings."
  }
}

Run-Git @("push", "-u", "origin", $branch)
Write-Host "Done. Your latest code has been pushed." -ForegroundColor Green
