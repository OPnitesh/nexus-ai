from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.db.engine import engine
from app.core.exceptions import EmailAlreadyExistsError
from app.modules.users.router import router as users_router
from app.modules.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting Nexus AI...")

    async with engine.begin() as connection:
        await connection.execute(text("SELECT 1"))

    print("Database Connected")

    yield

    print("Shutting down Nexus AI...")


app = FastAPI(
    title="Nexus AI",
    version="1.0.0",
    lifespan=lifespan,
)


app.include_router(users_router)
app.include_router(auth_router)


@app.exception_handler(EmailAlreadyExistsError)
async def email_already_exists_handler(
    request: Request,
    exc: EmailAlreadyExistsError,
):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "detail": str(exc),
        },
    )


@app.get("/")
async def root():
    return {
        "message": "Welcome to Nexus AI"
    }