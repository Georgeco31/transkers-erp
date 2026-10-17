# Arquitectura

Transker ERP es un monolito modular desplegado como tres contenedores:

```text
Navegador en LAN
  -> Next.js :3000 (único puerto productivo publicado)
     -> /api/* (proxy interno)
        -> FastAPI :8000 (red Docker interna)
           -> PostgreSQL :5432 (red Docker interna + volumen persistente)
```

## Backend

FastAPI expone `/api/v1`. Los endpoints validan entrada y autorización; `services.py` centraliza dinero, saldos, asignaciones y reportes. SQLAlchemy 2 administra persistencia y Alembic es la única vía productiva para cambiar el esquema.

Módulos: autenticación/usuarios, catálogos, viajes, gastos, cobranzas y reportes. La separación puede crecer por dominio sin dividir el despliegue.

## Frontend

Next.js App Router con TypeScript y Tailwind. El navegador nunca necesita conocer la IP de FastAPI: solicita rutas relativas `/api/v1/*`. La sesión se conserva en cookie HttpOnly. Las pantallas de operación usan navegación lateral en escritorio y menú táctil en móvil; las tablas cambian a tarjetas en viewports estrechos.

## Persistencia

`postgres_data` es un volumen Docker independiente del ciclo de los contenedores. `docker compose down` no lo elimina; ningún script normal utiliza `down -v`.

