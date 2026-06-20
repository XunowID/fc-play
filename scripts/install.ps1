# =============================================================================
# FC-Play Installer (Windows PowerShell)
# =============================================================================
# Invoke-Expression (Invoke-WebRequest -Uri "https://raw.githubusercontent.com/XunowID/fc-play/main/scripts/install.ps1").Content
#
# Or with extras:
#   ...install.ps1 -VoiceNim -VoiceLocal
# =============================================================================

param(
  [switch]$VoiceNim,
  [switch]$VoiceLocal,
  [switch]$VoiceAll,
  [string]$TorchBackend = "",
  [switch]$DryRun,
  [switch]$Help
)

function Show-Usage {
  Write-Host @"
Usage: install.ps1 [options]
  -VoiceNim      Install NVIDIA NIM voice support
  -VoiceLocal    Install local Whisper voice support
  -VoiceAll      Install both voice backends
  -TorchBackend  PyTorch backend (cpu/cuda)
  -DryRun        Print commands without executing
  -Help          Show this help
"@
  exit 0
}

if ($Help) { Show-Usage }

$REPO = "git+https://github.com/XunowID/fc-play.git"
$PYTHON_VERSION = "3.12"
$MIN_UV = "0.4.0"

function Step($msg) { Write-Host "`n✦ $msg" -ForegroundColor Cyan }
function Run($cmd) {
  Write-Host "  → $cmd" -ForegroundColor Gray
  if (-not $DryRun) {
    Invoke-Expression $cmd
    if ($LASTEXITCODE -and $LASTEXITCODE -ne 0) { throw "Command failed: $cmd" }
  }
}

# ─── Welcome ──────────────────────────────────────────────────────────
Write-Host @"

╔═══════════════════════════════════════════════╗
║        FC-Play — Zero Setup Installer          ║
║  Play with Claude — Free. Fast. Fabulous.      ║
╚═══════════════════════════════════════════════╝
"@ -ForegroundColor Magenta

# ─── 1. Ensure uv ──────────────────────────────────────────────────
Step "1/5 — Setting up uv..."
$uv = Get-Command "uv" -ErrorAction SilentlyContinue
if ($uv) {
  Write-Host "  ✓ uv found"
  Run "uv self update 2>null | Out-Null"
} else {
  Write-Host "  → Installing uv..."
  Run "powershell -ExecutionPolicy ByPass -c `"`$null = [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12; iex ((Invoke-WebRequest https://astral.sh/uv/install.ps1).Content)`""
  $env:Path = [Environment]::GetEnvironmentVariable("Path","User") + ";$env:Path"
}

# ─── 2. Install Python ────────────────────────────────────────────
Step "2/5 — Ensuring Python $PYTHON_VERSION..."
Run "uv python install $PYTHON_VERSION 2>null | Out-Null"
Write-Host "  ✓ Python $PYTHON_VERSION ready" -ForegroundColor Green

# ─── 3. Install FC-Play ──────────────────────────────────────────
Step "3/5 — Installing FC-Play..."
$extras = ""
if ($VoiceAll) {
  $extras = "[voice,voice_local]"
} elseif ($VoiceNim) {
  $extras = "[voice]"
} elseif ($VoiceLocal) {
  $extras = "[voice_local]"
}

$torchFlag = ""
if ($TorchBackend) {
  $torchFlag = "--torch-backend $TorchBackend"
}

Run "uv tool install --force '${REPO}${extras}' $torchFlag"

# ─── 4. Create config directory ──────────────────────────────────
Step "4/5 — Creating config directory..."
Run "New-Item -ItemType Directory -Force -Path `"$env:USERPROFILE\.fc-play`" | Out-Null"
$envPath = "$env:USERPROFILE\.fc-play\.env"
if (-not (Test-Path $envPath)) {
  Write-Host "  → Creating default .env..."
  Run "New-Item -ItemType File -Path '$envPath' -Force | Out-Null"
  @"
# FC-Play Configuration
CUSTOM_API_KEY=your-api-key-here
CUSTOM_API_MODEL=claude-sonnet-4-20250514
PORT=3010
"@ | Set-Content $envPath -Encoding UTF8
}
Write-Host "  ✓ Config at $envPath" -ForegroundColor Green

# ─── 5. Verify ──────────────────────────────────────────────────
Step "5/5 — Verifying installation..."
$fc = Get-Command "fc-play" -ErrorAction SilentlyContinue
if ($fc) {
  Write-Host "  ✓ fc-play installed!" -ForegroundColor Green
} else {
  Write-Host "  ⚠ fc-play not found. Try restarting your terminal." -ForegroundColor Yellow
}

# ─── Done ──────────────────────────────────────────────────────────
Write-Host @"

╔═══════════════════════════════════════════════╗
║         🎉 FC-Play is ready to go!            ║
╚═══════════════════════════════════════════════╝

  📝 Edit your config: notepad `"$env:USERPROFILE\.fc-play\.env`"

  🚀 Start the server:  fc-play server
  🖥️  Launch dashboard:  fc-play tui
  🌐 Open admin UI:     fc-play admin
  ℹ️  Check status:      fc-play status

  🔗 Add your API key:
     CUSTOM_API_KEY=sk-ant-...
     CUSTOM_API_MODEL=claude-sonnet-4-20250514
"@ -ForegroundColor Magenta
