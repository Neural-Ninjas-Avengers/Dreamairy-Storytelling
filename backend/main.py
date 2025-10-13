"""Main FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.api.endpoints import router as api_router
from app.api.websockets import ws_router


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    settings = get_settings()
    
    # Validate AWS configuration on startup
    if not settings.validate_aws_config():
        logger.warning(
            "AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY in your .env file before using AWS services."
        )
    
    logger.info(f"Starting Adaptive Storytelling Agent in {settings.environment} mode")
    logger.info(f"Demo mode: {settings.demo_mode}")
    
    if settings.offline_mode or settings.use_mock_services:
        logger.info("🎭 RUNNING IN OFFLINE MODE - NO AWS COSTS WILL BE INCURRED")
        logger.info("📚 Using mock services for story generation and emotion detection")
    else:
        logger.info("☁️ Running with real AWS services - costs may apply")
    
    yield
    
    # Cleanup on shutdown
    logger.info("Shutting down Adaptive Storytelling Agent")
    
    # Import here to avoid circular imports
    from app.api.endpoints import orchestrator
    await orchestrator.shutdown()


# Create FastAPI application
app = FastAPI(
    title="Adaptive Children's Storytelling Agent",
    description="AI-powered storytelling that adapts to children's emotions in real-time",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
settings = get_settings()

# More permissive CORS for development
if settings.environment == "development":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include API routers
app.include_router(api_router, prefix="/api/v1", tags=["Storytelling API"])
app.include_router(ws_router, prefix="/api/v1", tags=["WebSocket API"])

# Include demo router
from app.api.demo_endpoints import demo_router
app.include_router(demo_router, prefix="/api/v1", tags=["Demo API"])

# Serve demo static files
try:
    app.mount("/demo", StaticFiles(directory="demo", html=True), name="demo")
except Exception:
    logger.warning("Demo directory not found, demo interface not available")


@app.get("/")
async def root():
    """Root endpoint - redirect to new welcome page."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/demo/welcome.html")


@app.get("/info")
async def app_info():
    """Application information endpoint."""
    return {
        "message": "Adaptive Children's Storytelling Agent",
        "version": "1.0.0",
        "demo_mode": settings.demo_mode,
        "offline_mode": settings.offline_mode,
        "using_mock_services": settings.use_mock_services,
        "aws_configured": settings.validate_aws_config(),
        "cost_warning": "NO AWS COSTS" if (settings.offline_mode or settings.use_mock_services) else "AWS COSTS MAY APPLY",
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "api_base": "/api/v1",
            "websocket": "/api/v1/ws/{connection_id}",
            "demo": "/demo/welcome.html"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    return {
        "status": "healthy",
        "aws_configured": settings.validate_aws_config(),
        "demo_mode": settings.demo_mode,
        "environment": settings.environment
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=3001,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )