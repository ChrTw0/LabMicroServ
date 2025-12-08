"""
Billing Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal
from src.modules.billing.models import InvoiceType, InvoiceStatus


# ==================== Invoice Item Schemas ====================

class InvoiceItemResponse(BaseModel):
    """Schema for invoice item response"""
    id: int
    invoice_id: int
    service_code: Optional[str] = None
    service_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


# ==================== Invoice Schemas ====================

class InvoiceCreate(BaseModel):
    """Schema for creating an invoice from an order"""
    order_id: int = Field(..., gt=0, description="ID de la orden")
    invoice_type: InvoiceType = Field(..., description="Tipo de comprobante (BOLETA o FACTURA)")

    @validator('invoice_type')
    def validate_invoice_type(cls, v, values):
        """Validate invoice type"""
        if v not in [InvoiceType.BOLETA, InvoiceType.FACTURA]:
            raise ValueError('Tipo de comprobante inválido')
        return v


class InvoiceUpdateStatus(BaseModel):
    """Schema for updating invoice status"""
    invoice_status: InvoiceStatus = Field(..., description="Nuevo estado del comprobante")


class InvoiceResponse(BaseModel):
    """Schema for invoice response"""
    id: int
    invoice_number: str
    order_id: int
    patient_id: int
    location_id: int
    invoice_type: InvoiceType
    invoice_status: InvoiceStatus
    customer_document_type: str
    customer_document_number: str
    customer_name: str
    customer_address: Optional[str]
    subtotal: Decimal
    tax: Decimal
    total: Decimal
    issue_date: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class InvoiceDetailResponse(InvoiceResponse):
    """Detailed invoice response with items"""
    items: List[InvoiceItemResponse] = Field(default_factory=list)


class InvoiceListResponse(BaseModel):
    """Paginated list of invoices"""
    total: int = Field(..., description="Total de comprobantes")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    invoices: List[InvoiceResponse] = Field(..., description="Lista de comprobantes")


# ==================== Invoice Statistics ====================

class InvoiceStats(BaseModel):
    """Invoice statistics"""
    total_invoices: int = Field(..., description="Total de comprobantes")
    invoices_by_type: dict = Field(..., description="Comprobantes por tipo")
    invoices_by_status: dict = Field(..., description="Comprobantes por estado")
    total_billed: Decimal = Field(..., description="Total facturado")
