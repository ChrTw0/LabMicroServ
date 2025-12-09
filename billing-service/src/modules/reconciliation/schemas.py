"""
Reconciliation Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from src.modules.reconciliation.models import ClosureStatus


# ==================== Discrepancy Schemas ====================

class DiscrepancyResponse(BaseModel):
    """Schema for discrepancy response"""
    id: int
    closure_id: int
    description: str
    is_resolved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DiscrepancyCreate(BaseModel):
    """Schema for creating a discrepancy"""
    description: str = Field(..., min_length=1, description="Descripción de la discrepancia")


class DiscrepancyResolve(BaseModel):
    """Schema for resolving a discrepancy"""
    is_resolved: bool = Field(True, description="Marcar como resuelta")


# ==================== Daily Closure Schemas ====================

class DailyClosureCreate(BaseModel):
    """Schema for creating a daily closure"""
    location_id: int = Field(..., gt=0, description="ID de la sede")
    closure_date: date = Field(..., description="Fecha de cierre")
    registered_total: Decimal = Field(..., ge=0, description="Total registrado")


class DailyClosureResponse(BaseModel):
    """Schema for daily closure response"""
    id: int
    location_id: int
    closure_date: date
    status: ClosureStatus
    expected_total: Decimal
    registered_total: Decimal
    difference: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class DailyClosureDetailResponse(DailyClosureResponse):
    """Detailed daily closure response with discrepancies"""
    discrepancies: List[DiscrepancyResponse] = Field(default_factory=list)


class DailyClosureListResponse(BaseModel):
    """Paginated list of daily closures"""
    total: int = Field(..., description="Total de cierres")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    closures: List[DailyClosureResponse] = Field(..., description="Lista de cierres")


class DailyClosureReopen(BaseModel):
    """Schema for reopening a closure"""
    reason: str = Field(..., min_length=10, description="Justificación para reabrir (mínimo 10 caracteres)")


class ClosureStats(BaseModel):
    """Statistics for closures"""
    total_closures: int = Field(..., description="Total de cierres")
    open_closures: int = Field(..., description="Cierres abiertos")
    closed_closures: int = Field(..., description="Cierres cerrados")
    total_discrepancies: int = Field(..., description="Total de discrepancias")
    unresolved_discrepancies: int = Field(..., description="Discrepancias sin resolver")


# ==================== Reconciliation Report Schemas ====================

class PaymentMethodSummary(BaseModel):
    """Payment method summary for reconciliation"""
    payment_method: str = Field(..., description="Método de pago")
    expected_total: Decimal = Field(..., description="Total esperado del sistema")
    registered_total: Decimal = Field(..., description="Total registrado")
    difference: Decimal = Field(..., description="Diferencia")


class ReconciliationReport(BaseModel):
    """Complete reconciliation report - RF-057"""
    closure_date: date = Field(..., description="Fecha del cierre")
    location_id: int = Field(..., description="ID de la sede")
    total_orders: int = Field(..., description="Total de órdenes")
    total_invoices: int = Field(..., description="Total de comprobantes")
    total_payments: Decimal = Field(..., description="Total de pagos")
    total_billed: Decimal = Field(..., description="Total facturado")
    payment_methods: List[PaymentMethodSummary] = Field(..., description="Resumen por método de pago")
    discrepancies: List[DiscrepancyResponse] = Field(default_factory=list)
    has_discrepancies: bool = Field(..., description="Indica si hay discrepancias")
