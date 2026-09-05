import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes.auth import router as auth_router
from app.routes.games import router as games_router
from app.routes.reminders import router as reminders_router
from app.routes.dashboard import router as dashboard_router
from app.routes.language import router as language_router
from app.routes.voice_companion import router as voice_companion_router
from app.routes.reports import router as reports_router
from app.routes.compliance import router as compliance_router
from app.routes.patients import router as patients_router
from app.routes.sync import router as sync_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.validate_for_environment()
    job_task = None
    if settings.background_jobs_enabled:
        from app.jobs import start_in_background

        job_task = start_in_background()
    yield
    if job_task is not None:
        job_task.cancel()
        try:
            await job_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Innermost: rate limit. Outermost: CORS so 429s still carry ACAO headers.
app.add_middleware(RateLimitMiddleware)
_origins = settings.cors_origin_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers."""
    return {
        "status": "ok",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION,
        "environment": settings.ENVIRONMENT,
    }


app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(games_router, prefix=settings.API_V1_STR)
app.include_router(reminders_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)
app.include_router(language_router, prefix=settings.API_V1_STR)
app.include_router(voice_companion_router, prefix=settings.API_V1_STR)
app.include_router(reports_router, prefix=settings.API_V1_STR)
app.include_router(compliance_router, prefix=settings.API_V1_STR)
app.include_router(patients_router, prefix=settings.API_V1_STR)
app.include_router(sync_router, prefix=settings.API_V1_STR)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
