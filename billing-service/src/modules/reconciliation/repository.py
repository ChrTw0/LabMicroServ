"""
Reconciliation Repository (Data access layer)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List, Tuple
from datetime import date

from src.modules.reconciliation.models import DailyClosure, Discrepancy, ClosureStatus


class DailyClosureRepository:
    """Repository for DailyClosure operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        location_id: Optional[int] = None,
        status: Optional[ClosureStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[DailyClosure], int]:
        """Get all closures with filters and pagination"""
        query = select(DailyClosure)

        # Apply filters
        if location_id:
            query = query.where(DailyClosure.location_id == location_id)
        if status:
            query = query.where(DailyClosure.status == status)
        if date_from:
            query = query.where(DailyClosure.closure_date >= date_from)
        if date_to:
            query = query.where(DailyClosure.closure_date <= date_to)

        # Count total
        count_query = select(func.count()).select_from(query.alias())
        total = (await db.execute(count_query)).scalar()

        # Apply pagination
        query = query.offset((page - 1) * page_size).limit(page_size)
        query = query.order_by(DailyClosure.closure_date.desc())

        result = await db.execute(query)
        closures = result.scalars().all()

        return closures, total

    @staticmethod
    async def get_by_id(db: AsyncSession, closure_id: int) -> Optional[DailyClosure]:
        """Get closure by ID"""
        query = select(DailyClosure).where(DailyClosure.id == closure_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_discrepancies(db: AsyncSession, closure_id: int) -> Optional[DailyClosure]:
        """Get closure by ID with discrepancies loaded"""
        query = select(DailyClosure).where(DailyClosure.id == closure_id)
        result = await db.execute(query)
        closure = result.scalar_one_or_none()

        if closure:
            # Load discrepancies
            disc_query = select(Discrepancy).where(Discrepancy.closure_id == closure_id)
            disc_result = await db.execute(disc_query)
            closure.discrepancies = list(disc_result.scalars().all())

        return closure

    @staticmethod
    async def get_by_location_and_date(
        db: AsyncSession,
        location_id: int,
        closure_date: date
    ) -> Optional[DailyClosure]:
        """Get closure by location and date"""
        query = select(DailyClosure).where(
            and_(
                DailyClosure.location_id == location_id,
                DailyClosure.closure_date == closure_date
            )
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, closure: DailyClosure) -> DailyClosure:
        """Create a new closure"""
        db.add(closure)
        await db.commit()
        await db.refresh(closure)
        return closure

    @staticmethod
    async def update(db: AsyncSession, closure: DailyClosure) -> DailyClosure:
        """Update a closure"""
        await db.commit()
        await db.refresh(closure)
        return closure

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> dict:
        """Get closure statistics"""
        query = select(DailyClosure)

        if date_from:
            query = query.where(DailyClosure.closure_date >= date_from)
        if date_to:
            query = query.where(DailyClosure.closure_date <= date_to)

        result = await db.execute(query)
        closures = result.scalars().all()

        total_closures = len(closures)
        open_closures = sum(1 for c in closures if c.status == ClosureStatus.OPEN)
        closed_closures = sum(1 for c in closures if c.status == ClosureStatus.CLOSED)

        # Count discrepancies
        disc_query = select(Discrepancy)
        if date_from or date_to:
            # Join with closures to filter by date
            disc_query = disc_query.join(DailyClosure)
            if date_from:
                disc_query = disc_query.where(DailyClosure.closure_date >= date_from)
            if date_to:
                disc_query = disc_query.where(DailyClosure.closure_date <= date_to)

        disc_result = await db.execute(disc_query)
        discrepancies = disc_result.scalars().all()

        total_discrepancies = len(discrepancies)
        unresolved_discrepancies = sum(1 for d in discrepancies if not d.is_resolved)

        return {
            "total_closures": total_closures,
            "open_closures": open_closures,
            "closed_closures": closed_closures,
            "total_discrepancies": total_discrepancies,
            "unresolved_discrepancies": unresolved_discrepancies
        }


class DiscrepancyRepository:
    """Repository for Discrepancy operations"""

    @staticmethod
    async def create(db: AsyncSession, discrepancy: Discrepancy) -> Discrepancy:
        """Create a new discrepancy"""
        db.add(discrepancy)
        await db.commit()
        await db.refresh(discrepancy)
        return discrepancy

    @staticmethod
    async def create_many(db: AsyncSession, discrepancies: List[Discrepancy]) -> List[Discrepancy]:
        """Create multiple discrepancies"""
        db.add_all(discrepancies)
        await db.commit()
        for d in discrepancies:
            await db.refresh(d)
        return discrepancies

    @staticmethod
    async def get_by_id(db: AsyncSession, discrepancy_id: int) -> Optional[Discrepancy]:
        """Get discrepancy by ID"""
        query = select(Discrepancy).where(Discrepancy.id == discrepancy_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, discrepancy: Discrepancy) -> Discrepancy:
        """Update a discrepancy"""
        await db.commit()
        await db.refresh(discrepancy)
        return discrepancy

    @staticmethod
    async def get_by_closure(db: AsyncSession, closure_id: int) -> List[Discrepancy]:
        """Get all discrepancies for a closure"""
        query = select(Discrepancy).where(Discrepancy.closure_id == closure_id)
        result = await db.execute(query)
        return list(result.scalars().all())
