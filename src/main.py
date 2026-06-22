import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.config import settings
from src.core.logging import setup_logging
from src.api.routes import router as api_router

# Initialize logging configuration before building app instance
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage API startup and shutdown lifecycles.
    """
    logger.info(f"Starting {settings.APP_NAME} (v{settings.APP_VERSION}) backend service...")
    yield
    logger.info(f"Stopping {settings.APP_NAME} backend service...")

# Initialize FastAPI App
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes under root to support POST /research directly
app.include_router(api_router)

@app.get("/")
async def root() -> dict:
    """
    Root endpoint returning service metadata.
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check() -> dict:
    """
    Service availability status check.
    """
    return {"status": "healthy"}
