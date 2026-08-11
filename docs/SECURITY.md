# Seguridad

- Argon2 almacena contraseñas; la API nunca devuelve hashes.
- JWT de sesión se guarda en cookie HttpOnly, `SameSite=Lax`, con vencimiento configurable. `Secure` debe activarse al usar HTTPS.
- La autorización vive en FastAPI. La gestión de usuarios requiere rol `admin`; `operator` accede a la operación.
- Pydantic valida cuerpos y SQLAlchemy parametriza consultas.
- Secretos solo por `.env`, que Git ignora. No use los valores de ejemplo en producción.
- Producción publica únicamente Next.js. API y PostgreSQL quedan en la red Docker interna.
- Los logs no incluyen passwords, tokens ni hashes; los errores de base se registran en servidor y muestran un mensaje neutro al usuario.
- No existen borrados físicos de movimientos financieros.

## Limitaciones de V1

La instalación LAN por HTTP no cifra tráfico. Utilice una red privada confiable, cuentas individuales y bloqueo de sesión del servidor. Para acceso fuera de la LAN, no publique el puerto directamente: implemente HTTPS/VPN con revisión técnica. No se implementó recuperación automática de contraseña; un administrador crea usuarios nuevos.

