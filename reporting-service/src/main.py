"""
Reporting Service Main Application
FastAPI application for reports, analytics and data warehouse
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from src.core.config import settings

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/reporting-service.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# Create FastAPI app
app = FastAPI(
    title="Reporting Service API",
    description="Microservicio de reportes, analytics y data warehouse",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info(f"Starting {settings.service_name} on port {settings.port}")
    logger.info(f"Environment: {settings.environment}")
    logger.info("Reporting service ready - no local database (queries other services)")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.service_name}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "reporting-service",
        "version": "1.0.0",
        "status": "running",
        "features": ["dashboard", "reports", "analytics", "data-warehouse"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "reporting-service"
    }


# Import and include routers
# from src.routers import dashboard, reports, analytics
# app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
# app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
