$ErrorActionPreference = "Continue"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot
docker compose -f docker-compose.prod.yml ps
$Port = if ($env:WEB_PORT) { $env:WEB_PORT } else { "3000" }
try {
  $Response = Invoke-WebRequest -Uri "http://localhost:$Port/login" -TimeoutSec 5 -UseBasicParsing
  Write-Host "Web: OK ($($Response.StatusCode))" -ForegroundColor Green
} catch { Write-Host "Web: ERROR - $($_.Exception.Message)" -ForegroundColor Red }
$ApiContainer = docker compose -f docker-compose.prod.yml ps -q api
if ($ApiContainer) {
  docker compose -f docker-compose.prod.yml exec -T api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"
}

