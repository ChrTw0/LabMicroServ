"""
API Gateway Main Application
Unified entry point for all microservices
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
    "logs/api-gateway.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# Create FastAPI app
app = FastAPI(
    title="API Gateway",
    description="Unified API Gateway for Laboratory Microservices",
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
    logger.info("API Gateway ready - routing to microservices")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.service_name}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "api-gateway",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "user_service": settings.user_service_url,
            "patient_service": settings.patient_service_url,
            "order_service": settings.order_service_url,
            "billing_service": settings.billing_service_url,
            "configuration_service": settings.configuration_service_url
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-gateway"
    }


# Import and include routers (proxy routes to microservices)
# from src.routers import users, patients, orders, billing, config
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(patients.router, prefix="/api/v1/patients", tags=["Patients"])
# app.include_router(orders.router, prefix="/api/v1/orders", tags=["Orders"])
# app.include_router(billing.router, prefix="/api/v1/billing", tags=["Billing"])
# app.include_router(config.router, prefix="/api/v1/config", tags=["Configuration"])
