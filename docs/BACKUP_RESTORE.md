# Backup y restauración

Los respaldos reales se guardan en `backups/`, están ignorados por Git y deben copiarse periódicamente a un medio seguro distinto de la PC servidor.

## Crear y listar

```powershell
.\scripts\windows\backup-transker.ps1
Get-ChildItem .\backups\*.dump
```

El formato es `transker_AAAA-MM-DD_HHMM.dump`. El proceso usa `pg_dump -Fc` dentro del contenedor y copia el resultado al host.

## Verificar sin tocar producción

```powershell
.\scripts\windows\restore-transker.ps1 -Backup .\backups\transker_FECHA.dump -TestOnly
```

Se crea una base temporal, se restaura, se consulta su esquema y se elimina. La base productiva no se modifica.

## Restaurar producción

1. Haga un backup adicional del estado actual.
2. Ejecute `.\scripts\windows\restore-transker.ps1 -Backup RUTA.dump`.
3. El script exige escribir exactamente `RESTAURAR`, detiene web/API, restaura y los inicia nuevamente.
4. Ejecute `status-transker.ps1`, inicie sesión y verifique registros y reportes.

Nunca pruebe restauración destruyendo la base actual. Para respaldo diario, use Programador de tareas con `backup-transker.ps1` y una cuenta con acceso a Docker; configure retención en el almacenamiento externo sin borrar automáticamente el único backup disponible.

