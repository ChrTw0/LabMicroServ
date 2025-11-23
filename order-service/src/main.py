"""
Order Service Main Application
FastAPI application for order management (catalog, orders, lab integration)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from src.core.config import settings
from src.core.database import create_tables

# Configure logger
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
)
logger.add(
    "logs/order-service.log",
    rotation="500 MB",
    retention="10 days",
    level="INFO"
)

# Create FastAPI app
app = FastAPI(
    title="Order Service API",
    description="Microservicio de gestión de órdenes (catálogo, órdenes, integración laboratorio)",
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
    """Initialize database on startup"""
    logger.info(f"Starting {settings.service_name} on port {settings.port}")
    logger.info(f"Environment: {settings.environment}")

    # Create tables
    await create_tables()
    logger.info("Database tables created successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info(f"Shutting down {settings.service_name}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "order-service",
        "version": "1.0.0",
        "status": "running",
        "modules": ["catalog", "orders", "lab_integration"]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "order-service"
    }


# Import and include routers
from src.modules.catalog.router import category_router, service_router
from src.modules.orders.router import router as order_router
from src.modules.lab_integration.router import router as lab_sync_router

app.include_router(category_router)
app.include_router(service_router)
app.include_router(order_router)
app.include_router(lab_sync_router)
