# Transker ERP

Sistema web interno para administrar la operación diaria de Transker: clientes, choferes, vehículos, viajes, gastos, cobranzas, cuentas por cobrar y rentabilidad operativa registrada.

## Requisitos

- Docker Desktop con Docker Compose
- Git
- Navegador moderno

## Inicio rápido

1. Copie `.env.example` como `.env` y cambie todas las contraseñas y `SECRET_KEY`.
2. Ejecute `scripts/windows/start-transker.ps1` en Windows o `scripts/unix/start-transker.sh` en Linux/macOS.
3. Abra `http://localhost:3000`.

El único puerto publicado en producción es el de la web. La API y PostgreSQL permanecen en la red interna de Docker. Consulte `docs/DEPLOYMENT.md` para la instalación productiva y acceso desde la LAN.

## Desarrollo

```bash
docker compose up --build
```

API: `http://localhost:8000` (solo loopback en desarrollo). Web: `http://localhost:3000`.

## Pruebas

Consulte `docs/TESTING.md` para ejecutar pruebas de backend, lint, typecheck, build y el escenario integral.

