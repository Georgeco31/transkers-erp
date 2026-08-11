# Entrega y mantenimiento

## Operación diaria

- Inicio: `scripts/windows/start-transker.ps1`
- Estado: `scripts/windows/status-transker.ps1`
- Parada segura: `scripts/windows/stop-transker.ps1`
- Backup: `scripts/windows/backup-transker.ps1`
- Restauración: `scripts/windows/restore-transker.ps1`

## Credenciales bootstrap

El usuario y contraseña iniciales provienen de `ADMIN_USERNAME` y `ADMIN_PASSWORD` en `.env`. El seed solo crea el usuario si no existe; no sobrescribe su hash en ejecuciones posteriores. Cambie el secreto de ejemplo antes del primer arranque y no comparta `.env`.

## Evolución

Trabaje en `dev`, agregue cambios de esquema mediante Alembic y pruebas exactas con Decimal. Promueva a `main` solo tras completar la lista de `docs/TESTING.md`, validar respaldo/restauración temporal y confirmar acceso móvil. No use `docker compose down -v`.

## Diagnóstico

Use `status-transker.ps1` y `docker compose -f docker-compose.prod.yml logs --tail 200 api web db`. Nunca pegue logs que puedan contener información empresarial en canales públicos.

## Estado de esta instalación

- Web local: `http://localhost:3000`
- Web LAN: `http://192.168.100.219:3000` mientras la IP DHCP no cambie.
- Regla de firewall: `Transker ERP Web (Private LAN)`; TCP 3000, perfil privado, origen subred local.
- Servicios `db`, `api` y `web`: saludables tras reinicio.
- Backup limpio validado: `backups/transker_2026-08-11_0417.dump`.
- Pendiente externo: probar desde un teléfono real en la misma LAN y configurar/subir el repositorio privado de GitHub (GitHub CLI no está instalado).
