#!/usr/bin/env sh
set -eu
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$project_root"
stamp="$(date +%Y-%m-%d_%H%M)"
target="$project_root/backups/transker_$stamp.dump"
container_id="$(docker compose -f docker-compose.prod.yml ps -q db)"
[ -n "$container_id" ] || { echo "La base de datos no está iniciada."; exit 1; }
docker compose -f docker-compose.prod.yml exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc -f /tmp/transker_backup.dump'
docker cp "$container_id:/tmp/transker_backup.dump" "$target"
docker compose -f docker-compose.prod.yml exec -T db rm -f /tmp/transker_backup.dump
echo "Backup creado: $target"

