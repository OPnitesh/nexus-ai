from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.db.engine import engine
from app.modules.agents.router import router as agents_router
from app.modules.auth.router import router as auth_router
from app.modules.users.router import router as users_router
from app.core.redis.client import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Nexus AI...")

    try:
        async with engine.begin() as connection:
            await connection.execute(text("SELECT 1"))

        print("Database Connected")
        await redis_client.ping()
        print("Redis Connected")
        yield

    finally:
        await redis_client.aclose()
        await engine.dispose()
        print("Shutting down Nexus AI...")


app = FastAPI(
    title="Nexus AI",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(agents_router)


@app.get("/")
async def root():
    return {"message": "Welcome to Nexus AI"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
