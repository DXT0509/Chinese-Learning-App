from contextlib import asynccontextmanager
from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import DBAPIError
from sqlalchemy.exc import TimeoutError as DatabaseTimeout

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
        # Fixed categories only: exception messages can include SQL and credentials.
        category = "application"
        if isinstance(exc, DatabaseTimeout):
            category = "database_pool_timeout"
        elif isinstance(exc, DBAPIError):
            category = "database_connection" if exc.connection_invalidated else "database_operation"
        logger.error("server_failure_%s", category)
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
        started = perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["Cache-Control"] = "no-store"
            return response
        finally:
            # Route templates contain no actual attempt/user IDs or query values.
            route = getattr(request.scope.get("route"), "path", "")
            if settings.environment == "development" and route.startswith(
                ("/api/v1/me/srs/", "/me/srs/")
            ):
                logger.info(
                    "srs_request route=%s status=%d ms=%.2f",
                    route,
                    status,
                    (perf_counter() - started) * 1000,
                )

    app.include_router(health_router)
    return app


app = create_app()
