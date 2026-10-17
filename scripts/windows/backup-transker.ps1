$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot
if (-not (Test-Path -LiteralPath ".env")) { throw "Falta el archivo .env." }
$Stamp = Get-Date -Format "yyyy-MM-dd_HHmm"
$BackupDir = Join-Path $ProjectRoot "backups"
$BackupPath = Join-Path $BackupDir "transker_$Stamp.dump"
$ContainerId = docker compose -f docker-compose.prod.yml ps -q db
if (-not $ContainerId) { throw "La base de datos no está iniciada." }
docker compose -f docker-compose.prod.yml exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/transker_backup.dump'
if ($LASTEXITCODE -ne 0) { throw "pg_dump falló." }
docker cp "${ContainerId}:/tmp/transker_backup.dump" $BackupPath
docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_backup.dump
if (-not (Test-Path -LiteralPath $BackupPath)) { throw "No se creó el archivo de respaldo." }
Write-Host "Backup creado: $BackupPath" -ForegroundColor Green

