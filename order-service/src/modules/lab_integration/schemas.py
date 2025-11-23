"""
Lab Integration Schemas (Pydantic models for request/response validation)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from src.modules.lab_integration.models import SyncStatus


# ==================== Lab Sync Schemas ====================

class LabSyncRequest(BaseModel):
    """Schema for requesting lab sync"""
    order_id: int = Field(..., gt=0, description="ID de la orden a sincronizar")


class LabSyncResponse(BaseModel):
    """Schema for lab sync log response"""
    id: int
    order_id: int
    sync_status: SyncStatus
    attempt_count: int
    synced_at: Optional[datetime]

    class Config:
        from_attributes = True


class LabSyncListResponse(BaseModel):
    """Paginated list of sync logs"""
    total: int = Field(..., description="Total de logs")
    page: int = Field(..., description="Página actual")
    page_size: int = Field(..., description="Tamaño de página")
    logs: List[LabSyncResponse] = Field(..., description="Lista de logs")


class LabSyncStats(BaseModel):
    """Lab sync statistics"""
    total_syncs: int = Field(..., description="Total de sincronizaciones")
    syncs_by_status: dict = Field(..., description="Sincronizaciones por estado")
    failed_syncs: int = Field(..., description="Sincronizaciones fallidas")
