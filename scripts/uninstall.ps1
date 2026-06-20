# =============================================================================
# FC-Play Uninstaller (Windows PowerShell)
# =============================================================================

Write-Host "Removing FC-Play..." -ForegroundColor Yellow

# Remove uv tool
uv tool uninstall fc-play 2>$null | Out-Null

# Remove config directory
Remove-Item -Recurse -Force "$env:USERPROFILE\.fc-play" -ErrorAction SilentlyContinue

Write-Host "✅ FC-Play has been uninstalled." -ForegroundColor Green
Write-Host "   Config directory ~/.fc-play/ removed."
