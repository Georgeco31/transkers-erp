import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import auth, catalogs, expenses, payments, reports, trips, users
from app.database import SessionLocal

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("transker")

app = FastAPI(title="Transker ERP API", version="1.0.0", docs_url="/api/docs", openapi_url="/api/openapi.json")

for route in (auth.router, users.router, catalogs.router, trips.router, expenses.router, payments.router, reports.router):
    app.include_router(route, prefix="/api/v1")


@app.exception_handler(SQLAlchemyError)
async def database_error(_: Request, exc: SQLAlchemyError) -> JSONResponse:
    logger.exception("Database operation failed", exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": "No fue posible completar la operación. Intente nuevamente."})


@app.get("/health")
def health() -> dict[str, str]:
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}

