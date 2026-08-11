#!/usr/bin/env sh
set -eu
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$project_root"
command -v docker >/dev/null 2>&1 || { echo "Docker no está instalado."; exit 1; }
docker info >/dev/null 2>&1 || { echo "Docker no está iniciado."; exit 1; }
[ -f .env ] || { echo "Falta .env. Copie .env.example y cambie los secretos."; exit 1; }
docker compose -f docker-compose.prod.yml up -d --build
port="${WEB_PORT:-3000}"
attempt=0
while [ "$attempt" -lt 60 ]; do
  healthy=0
  for service in db api web; do
    container_id="$(docker compose -f docker-compose.prod.yml ps -q "$service")"
    if [ -n "$container_id" ] && [ "$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$container_id")" = "healthy" ]; then
      healthy=$((healthy + 1))
    fi
  done
  if [ "$healthy" -eq 3 ]; then
    echo "Transker ERP: http://localhost:$port"
    docker compose -f docker-compose.prod.yml ps
    exit 0
  fi
  attempt=$((attempt + 1)); sleep 3
done
docker compose -f docker-compose.prod.yml logs --tail 80
exit 1
