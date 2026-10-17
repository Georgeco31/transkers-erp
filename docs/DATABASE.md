# Base de datos

## Tablas

- `users`: credenciales hasheadas, rol y estado.
- `clients`: clientes sin RUC obligatorio.
- `drivers`: choferes identificados internamente por `id`; el nombre no es único.
- `vehicles`: placa normalizada y única.
- `trips`: viajes, relaciones, estado, precio y código humano.
- `trip_expense_categories`: catálogo extensible.
- `trip_expenses`: múltiples costos directos por viaje.
- `vehicle_expenses`: mantenimiento o reparación.
- `client_payments`: pagos recibidos.
- `payment_allocations`: distribución de pagos a viajes.

Todas las relaciones históricas usan foreign keys `RESTRICT`. Fechas, relaciones, estados, usuario, placa y código tienen índices. Los importes tienen restricciones de signo en base de datos.

## Migraciones

Revisión inicial: `20260811_0001`.

```bash
cd apps/api
alembic upgrade head
alembic current
alembic revision --autogenerate -m "descripción"
```

Revise siempre una migración autogenerada antes de aplicarla. Producción no llama `Base.metadata.create_all()`.

