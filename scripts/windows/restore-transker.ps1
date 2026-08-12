param([Parameter(Mandatory=$true)][string]$Backup, [switch]$TestOnly)
$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $ProjectRoot
$BackupPath = (Resolve-Path -LiteralPath $Backup).Path
if ([IO.Path]::GetExtension($BackupPath) -ne ".dump") { throw "El archivo debe tener extensión .dump." }
$ContainerId = docker compose -f docker-compose.prod.yml ps -q db
if (-not $ContainerId) { throw "La base de datos no está iniciada." }
$DbUser = (docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_USER).Trim()
$DbName = (docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_DB).Trim()
docker cp $BackupPath "${ContainerId}:/tmp/transker_restore.dump"
if ($TestOnly) {
  $TestDb = "transker_restore_test_$(Get-Date -Format 'yyyyMMddHHmmss')"
  try {
    docker compose -f docker-compose.prod.yml exec -T db createdb -U $DbUser $TestDb
    if ($LASTEXITCODE -ne 0) { throw "No se pudo crear la base temporal." }
    docker compose -f docker-compose.prod.yml exec -T db pg_restore -U $DbUser -d $TestDb --no-owner /tmp/transker_restore.dump
    if ($LASTEXITCODE -ne 0) { throw "No se pudo restaurar el backup en la base temporal." }
    docker compose -f docker-compose.prod.yml exec -T db psql -U $DbUser -d $TestDb -tAc "SELECT count(*) FROM users"
    if ($LASTEXITCODE -ne 0) { throw "No se pudo consultar la base restaurada." }
    Write-Host "Restauración verificada en base temporal $TestDb." -ForegroundColor Green
  } finally {
    docker compose -f docker-compose.prod.yml exec -T db dropdb -U $DbUser --if-exists $TestDb
    docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump
  }
  exit 0
}
$Confirmation = Read-Host "Esta acción reemplazará la base productiva. Escriba RESTAURAR para continuar"
if ($Confirmation -cne "RESTAURAR") { docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump; throw "Restauración cancelada." }
docker compose -f docker-compose.prod.yml stop api web
try {
  docker compose -f docker-compose.prod.yml exec -T db pg_restore -U $DbUser -d $DbName --clean --if-exists --no-owner /tmp/transker_restore.dump
  if ($LASTEXITCODE -ne 0) { throw "No se pudo restaurar la base productiva." }
  docker compose -f docker-compose.prod.yml run --rm --no-deps api python -m app.admin_credentials
  if ($LASTEXITCODE -ne 0) { throw "La base se restauró, pero no fue posible sincronizar el administrador con .env." }
} finally {
  docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump
  docker compose -f docker-compose.prod.yml start api web
}
Write-Host "Restauración completada. Ejecute status-transker.ps1." -ForegroundColor Green
