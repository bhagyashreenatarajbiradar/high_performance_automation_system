
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.routes import router
from src.database.database import create_tables, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(
    title="High-Performance Automation System",
    description="Enterprise Task Automation Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/")
async def home():
    return {
        "message": "Welcome to High-Performance Automation System",
        "status": "Running successfully"
    }


@app.get("/health")
async def health_check():
    return {"status": "Healthy"}
