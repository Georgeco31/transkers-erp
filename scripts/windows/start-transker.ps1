param([int]$TimeoutSeconds = 180)
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker no está instalado o no está en PATH." }
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw "Docker Desktop no está iniciado. Ábralo y vuelva a ejecutar este script." }
if (-not (Test-Path -LiteralPath ".env")) { throw "Falta .env. Copie .env.example como .env y cambie todos los secretos." }
docker compose -f docker-compose.prod.yml up -d --build
if ($LASTEXITCODE -ne 0) { throw "No fue posible levantar los servicios." }
$Deadline = (Get-Date).AddSeconds($TimeoutSeconds)
do {
  Start-Sleep -Seconds 3
  $Containers = docker compose -f docker-compose.prod.yml ps --format json | ConvertFrom-Json
  $Unhealthy = @($Containers | Where-Object { $_.Health -eq "unhealthy" })
  if ($Unhealthy.Count -gt 0) { docker compose -f docker-compose.prod.yml logs --tail 80; throw "Un servicio quedó en estado unhealthy." }
  $AllHealthy = @($Containers | Where-Object { $_.Service -in @("db", "api", "web") -and $_.Health -eq "healthy" }).Count -eq 3
} until ($AllHealthy -or (Get-Date) -gt $Deadline)
if (-not $AllHealthy) { docker compose -f docker-compose.prod.yml logs --tail 80; throw "Los servicios no estuvieron listos dentro del tiempo esperado." }
$Port = if ($env:WEB_PORT) { $env:WEB_PORT } else { "3000" }
$LanIp = Get-NetIPConfiguration -ErrorAction SilentlyContinue | Where-Object { $_.IPv4DefaultGateway -and $_.NetAdapter.Status -eq "Up" } | Select-Object -First 1 -ExpandProperty IPv4Address | Select-Object -ExpandProperty IPAddress
Write-Host "Transker ERP está iniciado." -ForegroundColor Green
Write-Host "Servidor: http://localhost:$Port"
if ($LanIp) { Write-Host "LAN: http://${LanIp}:$Port" }
docker compose -f docker-compose.prod.yml ps
