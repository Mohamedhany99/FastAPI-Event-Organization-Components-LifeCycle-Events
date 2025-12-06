from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routers import contract
from app.db.session import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(title="eo_tech_challenge", version="0.1.0", lifespan=lifespan)

# All api routers
app.include_router(contract.router)

@app.get("/")
async def root():
    return {"message": "Welcome to EO Tech Challenge API"}
