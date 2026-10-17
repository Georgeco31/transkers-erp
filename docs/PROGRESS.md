# Progreso de Transker ERP

| Bloque | Estado | Qué se implementó | Pruebas realizadas | Problemas encontrados | Commit |
|---|---|---|---|---|---|
| 0 — Bootstrap | Completado | Monorepo, Compose dev/prod, servicios, healthchecks y proxy interno | Tres servicios saludables en Docker | GitHub CLI ausente | `b5dbe0f`, `4a9b4d8` |
| 1 — DB y autenticación | Completado | SQLAlchemy, migración Alembic, Argon2, cookie HttpOnly, roles y seed | Login real; PostgreSQL; migración limpia; seed idempotente | Ninguno | `4a9b4d8` |
| 2–4 — Catálogos | Completado | CRUD lógico, fichas y UI para clientes, choferes y vehículos | Crear, editar, desactivar, duplicados y asociaciones | Ninguno en pruebas | `4a9b4d8`, `c2e9b6d` |
| 5–8 — Operación | Completado | Viajes, estados, gastos, mantenimiento, reparación, pagos y asignaciones | Flujos críticos y Decimal | Ninguno en pruebas | `4a9b4d8`, `c2e9b6d` |
| 9–10 — Reportes/dashboard | Completado | Mensual, clientes, vehículos, cartera y dashboard | Escenario obligatorio exacto | Ninguno en pruebas | `4a9b4d8`, `c2e9b6d` |
| 11 — Mobile/UX | Completado en software | Menú móvil, formularios táctiles y tablas como tarjetas | Viewport 390×844 en 6 flujos, sin overflow; navegación táctil | Prueba desde teléfono físico pendiente | `c2e9b6d` |
| 12–13 — Operación/backup | Completado | Compose interno, firewall privado, scripts Windows/Unix, backup y restore seguro | Reinicio saludable; backup real; restore temporal | Ninguno | `4a9b4d8`, `0f1b21a` |
| 14 — Integral | Completado localmente | Prueba API reproducible y smoke UI productivo; datos smoke retirados | 11 tests, 82%; lint; typecheck; build; npm audit 0; persistencia; LAN local | Confirmación desde otro dispositivo y publicación GitHub pendientes | `4a9b4d8`, `c2e9b6d`, `0f1b21a` |
