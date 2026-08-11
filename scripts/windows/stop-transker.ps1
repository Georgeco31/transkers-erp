$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot
docker compose -f docker-compose.prod.yml down
Write-Host "Transker ERP se detuvo sin borrar datos." -ForegroundColor Green

