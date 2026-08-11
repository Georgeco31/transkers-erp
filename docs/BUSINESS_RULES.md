# Reglas de negocio

## Dinero

- Todos los montos se reciben como `Decimal`, se almacenan como `NUMERIC(14,2)` y se redondean a dos decimales con `ROUND_HALF_UP`.
- Un viaje cancelado no genera ingreso, cuenta por cobrar ni utilidad.
- Un viaje completado requiere fecha, cliente, vehículo, chofer y precio mayor que cero.
- El margen de viaje es precio acordado menos la suma de sus gastos directos.

## Cobranzas

- Un pago se asigna por defecto a viajes completados pendientes del mismo cliente, del más antiguo al más reciente.
- La suma asignada nunca puede superar el pago ni el precio del viaje.
- Un excedente se conserva como saldo a favor no aplicado.
- Saldo por cobrar del cliente: viajes completados menos asignaciones.
- Saldo a favor: pagos recibidos menos asignaciones.
- No se puede cancelar un viaje con pagos asignados ni cambiar su cliente.

## Resultado del período

Un viaje pertenece al mes de `trip_date`; mantenimiento y reparación al mes de `expense_date`; cobros al mes de `payment_date`.

```text
UTILIDAD OPERATIVA REGISTRADA
= ingresos de viajes completados del período
- gastos directos de esos viajes
- mantenimientos del período
- reparaciones del período
```

No es utilidad neta contable. No incluye automáticamente impuestos, depreciación, nómina administrativa, alquiler, servicios, costos financieros ni partidas no registradas.

## Historial

No hay endpoints de eliminación física para viajes ni movimientos financieros. Clientes, choferes, vehículos y categorías se desactivan mediante `is_active`.

