from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import contract
from app.db.session import async_engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Tables created or already exist")

    yield


app = FastAPI(title="eo_tech_challenge", version="0.1.0", lifespan=lifespan)

# All api routers
app.include_router(contract.router)

@app.get("/")
async def root():
    return {"message": "Welcome to EO Tech Challenge API"}
