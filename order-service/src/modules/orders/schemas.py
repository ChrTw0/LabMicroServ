from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from decimal import Decimal
from datetime import datetime
from .models import OrderStatus

# --- Order Item Schemas ---

class OrderItemCreate(BaseModel):
    test_id: int = Field(..., gt=0)

class OrderItemResponse(BaseModel):
    id: int
    test_id: int
    test_name: str
    test_code: str
    price: Decimal

    class Config:
        orm_mode = True

# --- Order Payment Schemas ---

class OrderPaymentCreate(BaseModel):
    amount: Decimal = Field(..., gt=0)
    payment_method: str = Field(..., min_length=3, max_length=50)
    reference: Optional[str] = Field(None, max_length=255)

class OrderPaymentResponse(OrderPaymentCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# --- Order Schemas ---

class OrderCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    location_id: int = Field(..., gt=0)
    referring_doctor_name: Optional[str] = Field(None, max_length=255)
    discount: Decimal = Field(Decimal("0.0"), ge=0)
    items: List[OrderItemCreate] = Field(..., min_items=1)

class OrderUpdate(BaseModel):
    referring_doctor_name: Optional[str] = Field(None, max_length=255)

class OrderStatusUpdate(BaseModel):
    status: Optional[OrderStatus] = None

class OrderResponse(BaseModel):
    id: int
    order_code: str
    patient_id: int
    location_id: int
    referring_doctor_name: Optional[str]
    total_amount: Decimal
    discount: Decimal
    final_amount: Decimal
    status: OrderStatus
    created_by_user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True

class OrderDetailResponse(OrderResponse):
    items: List[OrderItemResponse]
    payments: List[OrderPaymentResponse]

    class Config:
        orm_mode = True

class OrderListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: List[OrderResponse]

class OrderStats(BaseModel):
    total_orders: int
    orders_by_status: Dict[str, int]
    total_revenue: Decimal