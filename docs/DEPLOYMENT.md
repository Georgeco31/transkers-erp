# Despliegue en la PC servidor

## Preparación

1. Instale e inicie Docker Desktop y habilite su arranque con Windows.
2. Copie `.env.example` como `.env`.
3. Reemplace `POSTGRES_PASSWORD`, `SECRET_KEY` y `ADMIN_PASSWORD`. Use una `SECRET_KEY` aleatoria de al menos 32 caracteres y contraseñas distintas.
4. Mantenga `COOKIE_SECURE=false` mientras el acceso sea HTTP en la LAN. Si instala HTTPS, cambie a `true`.
5. Desde PowerShell en la raíz ejecute `.\scripts\windows\start-transker.ps1`.

Las migraciones y seeds idempotentes se ejecutan antes de iniciar la API. Abra `http://localhost:3000`.

## Acceso LAN

El script muestra una IP local aproximada. Confirme con `ipconfig` y abra desde el teléfono `http://IP-DEL-SERVIDOR:3000`. El teléfono debe estar en la misma red y sin aislamiento de clientes Wi-Fi.

Si Windows bloquea el acceso, cree manualmente una regla de entrada únicamente para TCP 3000, perfil **Privado** y, cuando sea posible, limitada a la subred local. No abra 5432 ni 8000. No cambie el perfil de una red pública para resolverlo.

En la instalación validada se creó la regla `Transker ERP Web (Private LAN)` con esos límites. Si cambia el puerto, actualice o reemplace esa regla; no cree una segunda regla amplia.

Pruebe en el teléfono: login, dashboard, nuevo viaje, gasto, pago, ficha del cliente y reportes. Confirme que no haya desplazamiento horizontal de la página.

## Arranque automático

Docker Desktop puede arrancar al iniciar sesión y los servicios productivos usan `restart: unless-stopped`. Alternativamente cree una tarea del Programador de tareas que, después de iniciar Docker, ejecute PowerShell con:

```text
-NoProfile -ExecutionPolicy Bypass -File C:\ruta\transker-erp\scripts\windows\start-transker.ps1
```

Use una cuenta local autorizada y establezca el directorio inicial en la raíz del proyecto. No almacene credenciales en la tarea.

## Actualización

Respalde antes, obtenga una versión aprobada desde `main` y vuelva a ejecutar `start-transker.ps1`. No use versiones de `dev` en producción.
