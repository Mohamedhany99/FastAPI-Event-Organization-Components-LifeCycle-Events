from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import contract, event
from app.db.models import models as _models  # ensure models are imported so metadata is populated
from app.db.session import async_engine, Base
from app.infra.logging import configure_logging
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Configure logging early
    try:
        configure_logging("DEBUG" if settings.DEBUG else "INFO")
    except Exception:
        # Avoid failing startup due to logging config
        pass
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created or already exist")

    yield


app = FastAPI(title="eo_tech_challenge", version="0.1.0", lifespan=lifespan)

# All api routers
app.include_router(contract.router)
app.include_router(event.router)

@app.get("/")
async def root():
    return {"message": "Welcome to EO Tech Challenge API"}
