"""
Orders, Catalog & Lab Sync Router - Proxy to order-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1", tags=["Orders & Catalog"])


# ============================================
# ORDERS ENDPOINTS
# ============================================

@router.get("/orders", tags=["Orders"])
async def list_orders(request: Request) -> Response:
    """List all orders (with pagination and filters)"""
    target_url = f"{settings.order_service_url}/api/v1/orders"
    return await proxy_request(request, target_url)


@router.get("/orders/statistics", tags=["Orders"])
async def get_order_statistics(request: Request) -> Response:
    """Get order statistics"""
    target_url = f"{settings.order_service_url}/api/v1/orders/statistics"
    return await proxy_request(request, target_url)


@router.get("/orders/number/{order_number}", tags=["Orders"])
async def get_order_by_number(request: Request, order_number: str) -> Response:
    """Get order by order number"""
    target_url = f"{settings.order_service_url}/api/v1/orders/number/{order_number}"
    return await proxy_request(request, target_url)


@router.get("/orders/{order_id}", tags=["Orders"])
async def get_order(request: Request, order_id: int) -> Response:
    """Get order by ID"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}"
    return await proxy_request(request, target_url)


@router.post("/orders", tags=["Orders"])
async def create_order(request: Request) -> Response:
    """Create new order"""
    target_url = f"{settings.order_service_url}/api/v1/orders"
    return await proxy_request(request, target_url)


@router.put("/orders/{order_id}", tags=["Orders"])
async def update_order(request: Request, order_id: int) -> Response:
    """Update order by ID"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}"
    return await proxy_request(request, target_url)


@router.delete("/orders/{order_id}", tags=["Orders"])
async def delete_order(request: Request, order_id: int) -> Response:
    """Delete order by ID"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}"
    return await proxy_request(request, target_url)


@router.put("/orders/{order_id}/status", tags=["Orders"])
async def update_order_status(request: Request, order_id: int) -> Response:
    """Update order status"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}/status"
    return await proxy_request(request, target_url)


@router.post("/orders/{order_id}/payments", tags=["Orders"])
async def add_order_payment(request: Request, order_id: int) -> Response:
    """Add payment to order"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}/payments"
    return await proxy_request(request, target_url)


@router.get("/orders/{order_id}/payments", tags=["Orders"])
async def get_order_payments(request: Request, order_id: int) -> Response:
    """Get order payments"""
    target_url = f"{settings.order_service_url}/api/v1/orders/{order_id}/payments"
    return await proxy_request(request, target_url)


# ============================================
# SERVICES/CATALOG ENDPOINTS
# ============================================

@router.get("/services", tags=["Catalog"])
async def list_services(request: Request) -> Response:
    """List all services/exams"""
    target_url = f"{settings.order_service_url}/api/v1/services"
    return await proxy_request(request, target_url)


@router.get("/services/{service_id}", tags=["Catalog"])
async def get_service(request: Request, service_id: int) -> Response:
    """Get service by ID"""
    target_url = f"{settings.order_service_url}/api/v1/services/{service_id}"
    return await proxy_request(request, target_url)


@router.post("/services", tags=["Catalog"])
async def create_service(request: Request) -> Response:
    """Create new service"""
    target_url = f"{settings.order_service_url}/api/v1/services"
    return await proxy_request(request, target_url)


@router.put("/services/{service_id}", tags=["Catalog"])
async def update_service(request: Request, service_id: int) -> Response:
    """Update service by ID"""
    target_url = f"{settings.order_service_url}/api/v1/services/{service_id}"
    return await proxy_request(request, target_url)


@router.delete("/services/{service_id}", tags=["Catalog"])
async def delete_service(request: Request, service_id: int) -> Response:
    """Delete service by ID"""
    target_url = f"{settings.order_service_url}/api/v1/services/{service_id}"
    return await proxy_request(request, target_url)


@router.put("/services/{service_id}/price", tags=["Catalog"])
async def update_service_price(request: Request, service_id: int) -> Response:
    """Update service price"""
    target_url = f"{settings.order_service_url}/api/v1/services/{service_id}/price"
    return await proxy_request(request, target_url)


@router.get("/services/{service_id}/price-history", tags=["Catalog"])
async def get_service_price_history(request: Request, service_id: int) -> Response:
    """Get service price history"""
    target_url = f"{settings.order_service_url}/api/v1/services/{service_id}/price-history"
    return await proxy_request(request, target_url)


# ============================================
# CATEGORIES ENDPOINTS
# ============================================

@router.get("/categories", tags=["Catalog"])
async def list_categories(request: Request) -> Response:
    """List all service categories"""
    target_url = f"{settings.order_service_url}/api/v1/categories"
    return await proxy_request(request, target_url)


@router.get("/categories/{category_id}", tags=["Catalog"])
async def get_category(request: Request, category_id: int) -> Response:
    """Get category by ID"""
    target_url = f"{settings.order_service_url}/api/v1/categories/{category_id}"
    return await proxy_request(request, target_url)


@router.post("/categories", tags=["Catalog"])
async def create_category(request: Request) -> Response:
    """Create new category"""
    target_url = f"{settings.order_service_url}/api/v1/categories"
    return await proxy_request(request, target_url)


@router.put("/categories/{category_id}", tags=["Catalog"])
async def update_category(request: Request, category_id: int) -> Response:
    """Update category by ID"""
    target_url = f"{settings.order_service_url}/api/v1/categories/{category_id}"
    return await proxy_request(request, target_url)


@router.delete("/categories/{category_id}", tags=["Catalog"])
async def delete_category(request: Request, category_id: int) -> Response:
    """Delete category by ID"""
    target_url = f"{settings.order_service_url}/api/v1/categories/{category_id}"
    return await proxy_request(request, target_url)


# ============================================
# LAB SYNC (LIS INTEGRATION) ENDPOINTS
# ============================================

@router.get("/lab-sync", tags=["Lab Integration"])
async def list_lab_sync_logs(request: Request) -> Response:
    """List lab sync logs (with pagination and filters)"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync"
    return await proxy_request(request, target_url)


@router.get("/lab-sync/statistics", tags=["Lab Integration"])
async def get_lab_sync_statistics(request: Request) -> Response:
    """Get lab sync statistics"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync/statistics"
    return await proxy_request(request, target_url)


@router.get("/lab-sync/order/{order_id}", tags=["Lab Integration"])
async def get_lab_sync_by_order(request: Request, order_id: int) -> Response:
    """Get lab sync log by order ID"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync/order/{order_id}"
    return await proxy_request(request, target_url)


@router.get("/lab-sync/{log_id}", tags=["Lab Integration"])
async def get_lab_sync_by_id(request: Request, log_id: int) -> Response:
    """Get lab sync log by ID"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync/{log_id}"
    return await proxy_request(request, target_url)


@router.post("/lab-sync", tags=["Lab Integration"])
async def sync_order_to_lis(request: Request) -> Response:
    """Sync order to LIS (Laboratory Information System)"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync"
    return await proxy_request(request, target_url)


@router.post("/lab-sync/{log_id}/retry", tags=["Lab Integration"])
async def retry_lab_sync(request: Request, log_id: int) -> Response:
    """Retry failed lab sync"""
    target_url = f"{settings.order_service_url}/api/v1/lab-sync/{log_id}/retry"
    return await proxy_request(request, target_url)


# ============================================
# REPORTING ENDPOINTS
# ============================================

@router.get("/orders/reports/by-payment-method", tags=["Reports"])
async def get_payment_method_report(request: Request) -> Response:
    """Get sales report by payment method - RF-077"""
    target_url = f"{settings.order_service_url}/api/v1/orders/reports/by-payment-method"
    return await proxy_request(request, target_url)


@router.get("/orders/reports/top-services", tags=["Reports"])
async def get_top_services_report(request: Request) -> Response:
    """Get top services report - RF-076"""
    target_url = f"{settings.order_service_url}/api/v1/orders/reports/top-services"
    return await proxy_request(request, target_url)


@router.get("/orders/reports/monthly-revenue", tags=["Reports"])
async def get_monthly_revenue_report(request: Request) -> Response:
    """Get monthly revenue comparison - RF-079"""
    target_url = f"{settings.order_service_url}/api/v1/orders/reports/monthly-revenue"
    return await proxy_request(request, target_url)


@router.get("/orders/reports/patient-types", tags=["Reports"])
async def get_patient_types_report(request: Request) -> Response:
    """Get patient types report - RF-078"""
    target_url = f"{settings.order_service_url}/api/v1/orders/reports/patient-types"
    return await proxy_request(request, target_url)
