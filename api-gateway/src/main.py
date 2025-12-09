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

# CORS middleware - DEBE ir ANTES de los routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Middleware adicional para manejar OPTIONS requests
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response as StarletteResponse

class OptionsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method == "OPTIONS":
            return StarletteResponse(
                status_code=200,
                headers={
                    "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Max-Age": "3600",
                }
            )
        return await call_next(request)

app.add_middleware(OptionsMiddleware)


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
from src.routers import auth, users, roles, profile, patients, orders, billing, config

# User service routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(profile.router)

# Patient service router
app.include_router(patients.router)

# Order service routers (includes catalog, orders, and lab-sync)
app.include_router(orders.router)

# Billing service router
app.include_router(billing.router)

# Configuration service routers (includes locations, company, settings)
app.include_router(config.router)

logger.info("✅ All routers registered successfully")
