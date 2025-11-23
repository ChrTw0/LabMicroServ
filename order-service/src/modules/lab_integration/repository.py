"""
Lab Integration Repository (Database operations)
"""
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Tuple

from src.modules.lab_integration.models import LabSyncLog, SyncStatus


class LabSyncLogRepository:
    """Repository for LabSyncLog operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        sync_status: Optional[SyncStatus] = None
    ) -> Tuple[List[LabSyncLog], int]:
        """Get all sync logs with filters and pagination"""
        query = select(LabSyncLog)

        # Apply filters
        filters = []
        if sync_status is not None:
            filters.append(LabSyncLog.sync_status == sync_status)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(LabSyncLog)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(LabSyncLog.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    @staticmethod
    async def get_by_id(db: AsyncSession, log_id: int) -> Optional[LabSyncLog]:
        """Get sync log by ID"""
        query = select(LabSyncLog).where(LabSyncLog.id == log_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_order_id(db: AsyncSession, order_id: int) -> Optional[LabSyncLog]:
        """Get sync log by order ID"""
        query = select(LabSyncLog).where(LabSyncLog.order_id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, log: LabSyncLog) -> LabSyncLog:
        """Create a new sync log"""
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def update(db: AsyncSession, log: LabSyncLog) -> LabSyncLog:
        """Update sync log"""
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_statistics(db: AsyncSession) -> dict:
        """Get sync statistics"""
        # Total syncs
        query = select(func.count()).select_from(LabSyncLog)
        total_result = await db.execute(query)
        total_syncs = total_result.scalar() or 0

        # Syncs by status
        syncs_by_status = {}
        for status in SyncStatus:
            query = select(func.count()).select_from(LabSyncLog).where(
                LabSyncLog.sync_status == status
            )
            result = await db.execute(query)
            syncs_by_status[status.value] = result.scalar() or 0

        # Failed syncs
        query = select(func.count()).select_from(LabSyncLog).where(
            LabSyncLog.sync_status == SyncStatus.FAILED
        )
        failed_result = await db.execute(query)
        failed_syncs = failed_result.scalar() or 0

        return {
            "total_syncs": total_syncs,
            "syncs_by_status": syncs_by_status,
            "failed_syncs": failed_syncs
        }
