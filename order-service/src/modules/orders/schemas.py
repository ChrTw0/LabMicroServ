"""
Order Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from src.modules.orders.models import OrderStatus, PaymentMethod


# ==================== Order Item Schemas ====================

class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    service_id: int = Field(..., gt=0, description="ID del servicio")
    quantity: int = Field(default=1, ge=1, description="Cantidad")

    @validator('quantity')
    def validate_quantity(cls, v):
        """Validate quantity is positive"""
        if v <= 0:
            raise ValueError('La cantidad debe ser mayor a 0')
        return v


class OrderItemResponse(BaseModel):
    """Schema for order item response"""
    id: int
    order_id: int
    service_id: int
    service_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal

    class Config:
        from_attributes = True


# ==================== Order Payment Schemas ====================

class OrderPaymentCreate(BaseModel):
    """Schema for creating a payment"""
    payment_method: PaymentMethod = Field(..., description="Método de pago")
    amount: Decimal = Field(..., gt=0, decimal_places=2, description="Monto del pago")

    @validator('amount')
    def validate_amount(cls, v):
        """Validate amount is positive and has max 2 decimal places"""
        if v <= 0:
            raise ValueError('El monto debe ser mayor a 0')
        if v.as_tuple().exponent < -2:
            raise ValueError('El monto debe tener máximo 2 decimales')
        return v


class OrderPaymentResponse(BaseModel):
    """Schema for payment response"""
    id: int
    order_id: int
    payment_method: PaymentMethod
    amount: Decimal

    class Config:
        from_attributes = True


# ==================== Order Schemas ====================

class OrderCreate(BaseModel):
    """Schema for creating an order"""
    patient_id: int = Field(..., gt=0, description="ID del paciente")
    location_id: int = Field(..., gt=0, description="ID de la sede")
    items: List[OrderItemCreate] = Field(..., min_items=1, description="Items de la orden (mínimo 1)")

    @validator('items')
    def validate_items(cls, v):
        """Validate at least one item"""
        if not v or len(v) == 0:
            raise ValueError('La orden debe tener al menos un item')
        return v


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    location_id: Optional[int] = Field(None, gt=0, description="ID de la sede")


class OrderUpdateStatus(BaseModel):
    """Schema for updating order status"""
    status: OrderStatus = Field(..., description="Nuevo estado de la orden")


class OrderAddPayment(BaseModel):
    """Schema for adding payment to order"""
    payments: List[OrderPaymentCreate] = Field(..., min_items=1, description="Pagos a registrar (mínimo 1)")

    @validator('payments')
    def validate_payments(cls, v):
        """Validate at least one payment"""
        if not v or len(v) == 0:
            raise ValueError('Debe registrar al menos un pago')
        return v


class OrderResponse(BaseModel):
    """Schema for order response"""
    id: int
    order_number: str
    patient_id: int
    location_id: int
    status: OrderStatus
    total: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Detailed order response with items and payments"""
    items: List[OrderItemResponse] = Field(default_factory=list)
    payments: List[OrderPaymentResponse] = Field(default_factory=list)
    total_paid: Decimal = Field(..., description="Total pagado")
    balance: Decimal = Field(..., description="Saldo pendiente")


class OrderListResponse(BaseModel):
    """Paginated list of orders"""
    total: int = Field(..., description="Total de órdenes")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    orders: List[OrderResponse] = Field(..., description="Lista de órdenes")


# ==================== Order Statistics ====================

class OrderStats(BaseModel):
    """Order statistics"""
    total_orders: int = Field(..., description="Total de órdenes")
    orders_by_status: dict = Field(..., description="Órdenes por estado")
    total_revenue: Decimal = Field(..., description="Ingresos totales")
