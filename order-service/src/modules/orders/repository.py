"""
Order Repository (Database operations)
"""
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal

from src.modules.orders.models import Order, OrderItem, OrderPayment, OrderStatus


class OrderRepository:
    """Repository for Order operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        patient_id: Optional[int] = None,
        location_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[Order], int]:
        """Get all orders with filters and pagination"""
        query = select(Order)

        # Apply filters
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(Order.order_number.ilike(search_pattern))
        if patient_id is not None:
            filters.append(Order.patient_id == patient_id)
        if location_id is not None:
            filters.append(Order.location_id == location_id)
        if status is not None:
            filters.append(Order.status == status)
        if date_from is not None:
            filters.append(func.date(Order.created_at) >= date_from)
        if date_to is not None:
            filters.append(func.date(Order.created_at) <= date_to)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Order)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Order.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        orders = list(result.scalars().all())

        return orders, total

    @staticmethod
    async def get_by_id(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get order by ID"""
        query = select(Order).where(Order.id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_details(db: AsyncSession, order_id: int) -> Optional[Order]:
        """Get order by ID with items and payments"""
        query = (
            select(Order)
            .options(
                selectinload(Order.items),
                selectinload(Order.payments)
            )
            .where(Order.id == order_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_order_number(db: AsyncSession, order_number: str) -> Optional[Order]:
        """Get order by order number"""
        query = select(Order).where(Order.order_number == order_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, order: Order) -> Order:
        """Create a new order"""
        db.add(order)
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def update(db: AsyncSession, order: Order) -> Order:
        """Update order"""
        await db.commit()
        await db.refresh(order)
        return order

    @staticmethod
    async def generate_order_number(db: AsyncSession) -> str:
        """Generate unique order number"""
        # Format: ORD-YYYYMMDD-XXXX
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")

        # Get count of orders today
        query = select(func.count()).select_from(Order).where(
            func.date(Order.created_at) == today.date()
        )
        result = await db.execute(query)
        count = result.scalar() or 0

        sequence = str(count + 1).zfill(4)
        return f"ORD-{date_str}-{sequence}"

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> dict:
        """Get order statistics"""
        # Base filter
        filters = []
        if date_from:
            filters.append(func.date(Order.created_at) >= date_from)
        if date_to:
            filters.append(func.date(Order.created_at) <= date_to)

        # Total orders
        query = select(func.count()).select_from(Order)
        if filters:
            query = query.where(and_(*filters))
        total_result = await db.execute(query)
        total_orders = total_result.scalar() or 0

        # Orders by status
        orders_by_status = {}
        for status in OrderStatus:
            status_filters = filters + [Order.status == status]
            query = select(func.count()).select_from(Order).where(and_(*status_filters))
            result = await db.execute(query)
            orders_by_status[status.value] = result.scalar() or 0

        # Total revenue (only completed orders)
        revenue_filters = filters + [Order.status == OrderStatus.COMPLETADA]
        query = select(func.sum(Order.total)).select_from(Order)
        if revenue_filters:
            query = query.where(and_(*revenue_filters))
        revenue_result = await db.execute(query)
        total_revenue = revenue_result.scalar() or Decimal("0.00")

        return {
            "total_orders": total_orders,
            "orders_by_status": orders_by_status,
            "total_revenue": total_revenue
        }


class OrderItemRepository:
    """Repository for OrderItem operations"""

    @staticmethod
    async def create_many(db: AsyncSession, items: List[OrderItem]) -> List[OrderItem]:
        """Create multiple order items"""
        db.add_all(items)
        await db.flush()
        return items


class OrderPaymentRepository:
    """Repository for OrderPayment operations"""

    @staticmethod
    async def create_many(db: AsyncSession, payments: List[OrderPayment]) -> List[OrderPayment]:
        """Create multiple payments"""
        db.add_all(payments)
        await db.flush()
        return payments

    @staticmethod
    async def get_total_paid(db: AsyncSession, order_id: int) -> Decimal:
        """Get total amount paid for an order"""
        query = select(func.sum(OrderPayment.amount)).where(OrderPayment.order_id == order_id)
        result = await db.execute(query)
        return result.scalar() or Decimal("0.00")
