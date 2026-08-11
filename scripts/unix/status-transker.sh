#!/usr/bin/env sh
set -eu
project_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
cd "$project_root"
docker compose -f docker-compose.prod.yml ps
docker compose -f docker-compose.prod.yml exec -T api python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/health').read().decode())"

