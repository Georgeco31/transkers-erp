# Pruebas

## Backend

Desde la raíz, con un entorno virtual y dependencias de prueba instaladas:

```powershell
.\.venv\Scripts\python.exe -m pytest apps/api/tests --cov=app --cov-report=term-missing
```

Las pruebas usan SQLite aislado y recrean sus tablas; jamás apuntan a producción. Cubren autenticación, catálogos, asociaciones, estados, gastos, Decimal, pagos parciales/completos/multiviaje, sobreasignación, saldo a favor, reportes y el escenario de aceptación obligatorio.

## Migración limpia y seed

En un entorno de prueba, ejecute `alembic upgrade head`, `python -m app.seed` dos veces y compruebe que existe un solo admin y nueve categorías.

## Frontend

```powershell
Set-Location apps\web
npm run lint
npm run typecheck
npm run build
```

## Smoke integral

El test `test_mandatory_business_acceptance_scenario` reproduce dos viajes por $1.200, gastos directos por $470, mantenimiento por $100, reparación por $50, resultado operativo de $580, pago de $800 y saldo pendiente de $400.

Antes de aprobar producción también se debe ejecutar el mismo flujo en Docker y revisar manualmente los viewports de escritorio y teléfono.

