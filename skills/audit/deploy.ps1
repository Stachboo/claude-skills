# deploy.ps1 — link this project into the Claude Code user skills dir
$src = $PSScriptRoot
$dest = Join-Path $env:USERPROFILE ".claude\skills\audit"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
New-Item -ItemType Junction -Path $dest -Target $src | Out-Null
Write-Host "Linked $dest -> $src"
