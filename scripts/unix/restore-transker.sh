#!/usr/bin/env sh
set -eu
[ "$#" -ge 1 ] || { echo "Uso: restore-transker.sh ARCHIVO.dump [--test]"; exit 1; }
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$project_root"
backup="$(CDPATH= cd -- "$(dirname -- "$1")" && pwd)/$(basename -- "$1")"
[ -f "$backup" ] || { echo "No existe el backup."; exit 1; }
container_id="$(docker compose -f docker-compose.prod.yml ps -q db)"
db_user="$(docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_USER)"
db_name="$(docker compose -f docker-compose.prod.yml exec -T db printenv POSTGRES_DB)"
docker cp "$backup" "$container_id:/tmp/transker_restore.dump"
if [ "${2:-}" = "--test" ]; then
  test_db="transker_restore_test_$(date +%Y%m%d%H%M%S)"
  cleanup_test_db() {
    docker compose -f docker-compose.prod.yml exec -T db dropdb -U "$db_user" --if-exists "$test_db"
    docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump
  }
  trap cleanup_test_db EXIT
  docker compose -f docker-compose.prod.yml exec -T db createdb -U "$db_user" "$test_db"
  docker compose -f docker-compose.prod.yml exec -T db pg_restore -U "$db_user" -d "$test_db" --no-owner /tmp/transker_restore.dump
  docker compose -f docker-compose.prod.yml exec -T db psql -U "$db_user" -d "$test_db" -tAc "SELECT count(*) FROM users"
  echo "Restauración temporal verificada."
  exit 0
fi
printf "Esta acción reemplazará la base productiva. Escriba RESTAURAR: "
read -r confirmation
[ "$confirmation" = "RESTAURAR" ] || { docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump; echo "Cancelado."; exit 1; }
docker compose -f docker-compose.prod.yml stop api web
docker compose -f docker-compose.prod.yml exec -T db pg_restore -U "$db_user" -d "$db_name" --clean --if-exists --no-owner /tmp/transker_restore.dump
docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_restore.dump
docker compose -f docker-compose.prod.yml start api web
echo "Restauración completada."
