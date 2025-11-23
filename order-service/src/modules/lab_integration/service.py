"""
Lab Integration Service (Business logic for LIS sync)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime
import httpx
from loguru import logger

from src.modules.lab_integration.models import LabSyncLog, SyncStatus
from src.modules.lab_integration.repository import LabSyncLogRepository
from src.modules.lab_integration.schemas import (
    LabSyncRequest, LabSyncResponse, LabSyncListResponse, LabSyncStats
)
from src.modules.orders.models import Order, OrderStatus
from sqlalchemy import select


class LabSyncService:
    """
    Service for Lab Integration System synchronization

    PENDIENTE DE INTEGRACIÓN REAL:
    ================================
    Este servicio está preparado para integrarse con un sistema LIS externo.
    Por ahora, todas las sincronizaciones se marcan como SUCCESS automáticamente.

    PASOS PARA INTEGRAR CON LIS REAL:
    ----------------------------------
    1. Configurar la URL del LIS real en LIS_API_URL (línea 27)
    2. Implementar la llamada HTTP real en sync_order_to_lis() (línea 67-96)
    3. Ajustar el payload según la API del LIS que se integre
    4. Manejar respuestas y errores específicos del LIS
    5. Configurar autenticación si el LIS lo requiere (API key, OAuth, etc.)

    REFERENCIAS:
    - Documentación del LIS a integrar: [PENDIENTE]
    - Credenciales de acceso: [PENDIENTE - configurar en variables de entorno]
    """

    # TODO: Configure this URL when integrating with real LIS
    # Replace with actual LIS API endpoint
    LIS_API_URL = "https://api.lis-system.com/v1"  # Placeholder

    @staticmethod
    async def sync_order_to_lis(
        db: AsyncSession,
        data: LabSyncRequest
    ) -> LabSyncResponse:
        """
        Sync an order to external LIS

        This method creates a sync log and will call the external LIS API
        when the integration is configured.
        """
        order_id = data.order_id

        # Validate order exists
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )

        # Check if order is in valid status for sync
        if order.status not in [OrderStatus.COMPLETADA, OrderStatus.EN_PROCESO]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La orden debe estar en estado COMPLETADA o EN_PROCESO para sincronizar. Estado actual: {order.status.value}"
            )

        # Check if already synced successfully
        existing_log = await LabSyncLogRepository.get_by_order_id(db, order_id)
        if existing_log and existing_log.sync_status == SyncStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"La orden {order_id} ya fue sincronizada exitosamente"
            )

        # Create or update sync log
        if existing_log:
            # Update existing log for retry
            existing_log.sync_status = SyncStatus.PENDING
            existing_log.attempt_count += 1
            existing_log.synced_at = None
            sync_log = await LabSyncLogRepository.update(db, existing_log)
        else:
            # Create new sync log
            sync_log = LabSyncLog(
                order_id=order_id,
                sync_status=SyncStatus.PENDING,
                attempt_count=1,
                synced_at=None
            )
            sync_log = await LabSyncLogRepository.create(db, sync_log)

        # =================================================================
        # TODO: INTEGRACIÓN REAL CON LIS - REEMPLAZAR ESTE BLOQUE
        # =================================================================
        # Cuando integres con el LIS real, reemplaza el código de simulación
        # (líneas 134-137) con el siguiente código de ejemplo (ajustado a tu LIS):
        #
        # try:
        #     async with httpx.AsyncClient() as client:
        #         # Preparar payload según especificaciones del LIS
        #         lis_payload = {
        #             "order_id": order.id,
        #             "order_number": order.order_number,
        #             "patient_id": order.patient_id,
        #             "patient_name": "...",  # Fetch from patient-service if needed
        #             "tests": [
        #                 {
        #                     "service_id": item.service_id,
        #                     "service_name": item.service_name,
        #                     "quantity": item.quantity
        #                 }
        #                 for item in order.items
        #             ],
        #             "priority": "NORMAL",  # Adjust based on order
        #             "notes": order.notes
        #         }
        #
        #         # Agregar headers de autenticación si es necesario
        #         headers = {
        #             "Authorization": f"Bearer {settings.LIS_API_KEY}",  # Configure in .env
        #             "Content-Type": "application/json"
        #         }
        #
        #         # Realizar llamada al LIS
        #         response = await client.post(
        #             f"{LabSyncService.LIS_API_URL}/orders",
        #             json=lis_payload,
        #             headers=headers,
        #             timeout=30.0
        #         )
        #         response.raise_for_status()
        #
        #         # Procesar respuesta del LIS
        #         lis_response = response.json()
        #         logger.info(f"Order {order_id} synced successfully to LIS. LIS ID: {lis_response.get('lis_order_id')}")
        #
        #         # Update sync log as SUCCESS
        #         sync_log.sync_status = SyncStatus.SUCCESS
        #         sync_log.synced_at = datetime.now()
        #         # Opcionalmente guardar el ID del LIS en el log
        #         # sync_log.lis_reference = lis_response.get('lis_order_id')
        #         sync_log = await LabSyncLogRepository.update(db, sync_log)
        #
        # except httpx.HTTPStatusError as e:
        #     logger.error(f"HTTP error syncing order {order_id} to LIS: {e.response.status_code} - {e.response.text}")
        #     sync_log.sync_status = SyncStatus.FAILED
        #     sync_log = await LabSyncLogRepository.update(db, sync_log)
        #     raise HTTPException(
        #         status_code=status.HTTP_502_BAD_GATEWAY,
        #         detail=f"Error del LIS: {e.response.text}"
        #     )
        # except httpx.RequestError as e:
        #     logger.error(f"Network error syncing order {order_id} to LIS: {e}")
        #     sync_log.sync_status = SyncStatus.FAILED
        #     sync_log = await LabSyncLogRepository.update(db, sync_log)
        #     raise HTTPException(
        #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        #         detail=f"No se pudo conectar con el LIS: {str(e)}"
        #     )
        # =================================================================

        # SIMULACIÓN TEMPORAL - ELIMINAR CUANDO SE INTEGRE LIS REAL
        logger.warning(f"⚠️  SIMULACIÓN: Sincronizando orden {order_id} al LIS (integración real pendiente)")
        sync_log.sync_status = SyncStatus.SUCCESS
        sync_log.synced_at = datetime.now()
        sync_log = await LabSyncLogRepository.update(db, sync_log)

        return LabSyncResponse.model_validate(sync_log)

    @staticmethod
    async def get_all_sync_logs(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        sync_status: Optional[SyncStatus] = None
    ) -> LabSyncListResponse:
        """Get all sync logs with pagination and filters"""
        logs, total = await LabSyncLogRepository.get_all(
            db=db,
            page=page,
            page_size=page_size,
            sync_status=sync_status
        )

        return LabSyncListResponse(
            total=total,
            page=page,
            page_size=page_size,
            logs=[LabSyncResponse.model_validate(log) for log in logs]
        )

    @staticmethod
    async def get_sync_log_by_id(
        db: AsyncSession,
        log_id: int
    ) -> LabSyncResponse:
        """Get sync log by ID"""
        log = await LabSyncLogRepository.get_by_id(db, log_id)

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Log de sincronización con ID {log_id} no encontrado"
            )

        return LabSyncResponse.model_validate(log)

    @staticmethod
    async def get_sync_log_by_order(
        db: AsyncSession,
        order_id: int
    ) -> LabSyncResponse:
        """Get sync log by order ID"""
        log = await LabSyncLogRepository.get_by_order_id(db, order_id)

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró log de sincronización para la orden {order_id}"
            )

        return LabSyncResponse.model_validate(log)

    @staticmethod
    async def retry_sync(
        db: AsyncSession,
        log_id: int
    ) -> LabSyncResponse:
        """Retry a failed sync"""
        log = await LabSyncLogRepository.get_by_id(db, log_id)

        if not log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Log de sincronización con ID {log_id} no encontrado"
            )

        if log.sync_status == SyncStatus.SUCCESS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede reintentar una sincronización exitosa"
            )

        # Retry sync by calling sync_order_to_lis
        return await LabSyncService.sync_order_to_lis(
            db,
            LabSyncRequest(order_id=log.order_id)
        )

    @staticmethod
    async def get_statistics(db: AsyncSession) -> LabSyncStats:
        """Get sync statistics"""
        stats = await LabSyncLogRepository.get_statistics(db)
        return LabSyncStats(**stats)
