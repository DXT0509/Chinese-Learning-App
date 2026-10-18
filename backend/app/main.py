from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.endpoints.authentication import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.learning import router as learning_router
from app.api.v1.router import router
from app.core.config import get_settings
from app.core.database import engine
from app.core.logging import configure_logging
from app.schemas.health import ErrorResponse

logger = configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application_started")
    yield
    await engine.dispose()
    logger.info("application_stopped")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
        responses={500: {"model": ErrorResponse}},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.exception_handler(Exception)
    async def unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_server_error")
        return JSONResponse(status_code=500, content={"detail": "Internal server error"})

    app.include_router(router)
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(learning_router, prefix="/api/v1")

    @app.exception_handler(RequestValidationError)
    async def invalid_input(request: Request, exc: RequestValidationError):
        # Default validation errors echo input, including credentials.
        return JSONResponse(status_code=422, content={"detail": "Invalid request"})

    @app.middleware("http")
    async def private_responses(request: Request, call_next):
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(health_router)
    return app


app = create_app()
