"""
Catalog Repository (Database operations)
"""
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from decimal import Decimal

from src.modules.catalog.models import Category, Service, PriceHistory


# ==================== Category Repository ====================

class CategoryRepository:
    """Repository for Category operations"""

    @staticmethod
    async def get_all(db: AsyncSession, active_only: bool = False) -> List[Category]:
        """Get all categories"""
        query = select(Category)
        if active_only:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.name)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        query = select(Category).where(Category.id == category_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Category]:
        """Get category by name"""
        query = select(Category).where(Category.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, category: Category) -> Category:
        """Create a new category"""
        db.add(category)
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def update(db: AsyncSession, category: Category) -> Category:
        """Update category"""
        await db.commit()
        await db.refresh(category)
        return category

    @staticmethod
    async def delete(db: AsyncSession, category: Category) -> None:
        """Delete category"""
        await db.delete(category)
        await db.commit()

    @staticmethod
    async def get_services_count(db: AsyncSession, category_id: int) -> int:
        """Get number of services in a category"""
        query = select(func.count(Service.id)).where(Service.category_id == category_id)
        result = await db.execute(query)
        return result.scalar() or 0

    @staticmethod
    async def get_all_with_services_count(
        db: AsyncSession,
        active_only: bool = False
    ) -> List[Tuple[Category, int]]:
        """Get all categories with service count"""
        query = (
            select(Category, func.count(Service.id).label('services_count'))
            .outerjoin(Service, Category.id == Service.category_id)
            .group_by(Category.id)
        )
        if active_only:
            query = query.where(Category.is_active == True)
        query = query.order_by(Category.name)

        result = await db.execute(query)
        return [(row[0], row[1]) for row in result.all()]


# ==================== Service Repository ====================

class ServiceRepository:
    """Repository for Service operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ) -> Tuple[List[Service], int]:
        """Get all services with filters and pagination"""
        # Base query with category relationship
        query = select(Service).options(selectinload(Service.category))

        # Apply filters
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Service.name.ilike(search_pattern),
                    Service.description.ilike(search_pattern)
                )
            )
        if category_id is not None:
            filters.append(Service.category_id == category_id)
        if is_active is not None:
            filters.append(Service.is_active == is_active)
        if min_price is not None:
            filters.append(Service.current_price >= min_price)
        if max_price is not None:
            filters.append(Service.current_price <= max_price)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Service)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Service.name)
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        services = list(result.scalars().all())

        return services, total

    @staticmethod
    async def get_by_id(db: AsyncSession, service_id: int) -> Optional[Service]:
        """Get service by ID with category"""
        query = (
            select(Service)
            .options(selectinload(Service.category))
            .where(Service.id == service_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Service]:
        """Get service by name"""
        query = select(Service).where(Service.name == name)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, service: Service) -> Service:
        """Create a new service"""
        db.add(service)
        await db.commit()
        await db.refresh(service)
        # Load category relationship
        await db.refresh(service, ['category'])
        return service

    @staticmethod
    async def update(db: AsyncSession, service: Service) -> Service:
        """Update service"""
        await db.commit()
        await db.refresh(service)
        # Load category relationship
        await db.refresh(service, ['category'])
        return service

    @staticmethod
    async def delete(db: AsyncSession, service: Service) -> None:
        """Delete service (soft delete by setting is_active=False)"""
        service.is_active = False
        await db.commit()


# ==================== Price History Repository ====================

class PriceHistoryRepository:
    """Repository for PriceHistory operations"""

    @staticmethod
    async def create(db: AsyncSession, price_history: PriceHistory) -> PriceHistory:
        """Create a new price history record"""
        db.add(price_history)
        await db.commit()
        await db.refresh(price_history)
        return price_history

    @staticmethod
    async def get_by_service_id(
        db: AsyncSession,
        service_id: int,
        limit: int = 10
    ) -> List[PriceHistory]:
        """Get price history for a service"""
        query = (
            select(PriceHistory)
            .where(PriceHistory.service_id == service_id)
            .order_by(PriceHistory.changed_at.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def get_all_history(
        db: AsyncSession,
        service_id: int
    ) -> List[PriceHistory]:
        """Get complete price history for a service"""
        query = (
            select(PriceHistory)
            .where(PriceHistory.service_id == service_id)
            .order_by(PriceHistory.changed_at.desc())
        )
        result = await db.execute(query)
        return list(result.scalars().all())
