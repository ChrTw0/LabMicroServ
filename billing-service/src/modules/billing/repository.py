"""
Billing Repository (Database operations)
"""
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from datetime import datetime, date
from decimal import Decimal

from src.modules.billing.models import Invoice, InvoiceItem, InvoiceType, InvoiceStatus


class InvoiceRepository:
    """Repository for Invoice operations"""

    @staticmethod
    async def get_all(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        invoice_type: Optional[InvoiceType] = None,
        invoice_status: Optional[InvoiceStatus] = None,
        patient_id: Optional[int] = None,
        location_id: Optional[int] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> Tuple[List[Invoice], int]:
        """Get all invoices with filters and pagination"""
        query = select(Invoice)

        # Apply filters
        filters = []
        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    Invoice.invoice_number.ilike(search_pattern),
                    Invoice.customer_name.ilike(search_pattern),
                    Invoice.customer_document_number.ilike(search_pattern)
                )
            )
        if invoice_type is not None:
            filters.append(Invoice.invoice_type == invoice_type)
        if invoice_status is not None:
            filters.append(Invoice.invoice_status == invoice_status)
        if patient_id is not None:
            filters.append(Invoice.patient_id == patient_id)
        if location_id is not None:
            filters.append(Invoice.location_id == location_id)
        if date_from is not None:
            filters.append(func.date(Invoice.issue_date) >= date_from)
        if date_to is not None:
            filters.append(func.date(Invoice.issue_date) <= date_to)

        if filters:
            query = query.where(and_(*filters))

        # Get total count
        count_query = select(func.count()).select_from(Invoice)
        if filters:
            count_query = count_query.where(and_(*filters))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Invoice.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await db.execute(query)
        invoices = list(result.scalars().all())

        return invoices, total

    @staticmethod
    async def get_by_id(db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID"""
        query = select(Invoice).where(Invoice.id == invoice_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id_with_items(db: AsyncSession, invoice_id: int) -> Optional[Invoice]:
        """Get invoice by ID with items"""
        query = (
            select(Invoice)
            .options(selectinload(Invoice.items))
            .where(Invoice.id == invoice_id)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_invoice_number(db: AsyncSession, invoice_number: str) -> Optional[Invoice]:
        """Get invoice by invoice number"""
        query = select(Invoice).where(Invoice.invoice_number == invoice_number)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_order_id(db: AsyncSession, order_id: int) -> Optional[Invoice]:
        """Get invoice by order ID"""
        query = select(Invoice).where(Invoice.order_id == order_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_order_id(db: AsyncSession, order_id: int) -> List[Invoice]:
        """Get all invoices for a specific order ID"""
        query = select(Invoice).where(Invoice.order_id == order_id)
        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def create(db: AsyncSession, invoice: Invoice) -> Invoice:
        """Create a new invoice"""
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def update(db: AsyncSession, invoice: Invoice) -> Invoice:
        """Update invoice"""
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def generate_invoice_number(
        db: AsyncSession,
        invoice_type: InvoiceType
    ) -> str:
        """Generate unique invoice number"""
        # Format: B001-00000001 (Boleta) or F001-00000001 (Factura)
        prefix = "B" if invoice_type == InvoiceType.BOLETA else "F"
        serie = "001"

        # Get count of invoices of this type
        query = select(func.count()).select_from(Invoice).where(
            Invoice.invoice_type == invoice_type
        )
        result = await db.execute(query)
        count = result.scalar() or 0

        sequence = str(count + 1).zfill(8)
        return f"{prefix}{serie}-{sequence}"

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> dict:
        """Get invoice statistics"""
        # Base filter
        filters = []
        if date_from:
            filters.append(func.date(Invoice.issue_date) >= date_from)
        if date_to:
            filters.append(func.date(Invoice.issue_date) <= date_to)

        # Total invoices
        query = select(func.count()).select_from(Invoice)
        if filters:
            query = query.where(and_(*filters))
        total_result = await db.execute(query)
        total_invoices = total_result.scalar() or 0

        # Invoices by type
        invoices_by_type = {}
        for inv_type in InvoiceType:
            type_filters = filters + [Invoice.invoice_type == inv_type]
            query = select(func.count()).select_from(Invoice).where(and_(*type_filters))
            result = await db.execute(query)
            invoices_by_type[inv_type.value] = result.scalar() or 0

        # Invoices by status
        invoices_by_status = {}
        for inv_status in InvoiceStatus:
            status_filters = filters + [Invoice.invoice_status == inv_status]
            query = select(func.count()).select_from(Invoice).where(and_(*status_filters))
            result = await db.execute(query)
            invoices_by_status[inv_status.value] = result.scalar() or 0

        # Total billed (only accepted invoices)
        billed_filters = filters + [Invoice.invoice_status == InvoiceStatus.ACCEPTED]
        query = select(func.sum(Invoice.total)).select_from(Invoice)
        if billed_filters:
            query = query.where(and_(*billed_filters))
        billed_result = await db.execute(query)
        total_billed = billed_result.scalar() or Decimal("0.00")

        return {
            "total_invoices": total_invoices,
            "invoices_by_type": invoices_by_type,
            "invoices_by_status": invoices_by_status,
            "total_billed": total_billed
        }


class InvoiceItemRepository:
    """Repository for InvoiceItem operations"""

    @staticmethod
    async def create_many(db: AsyncSession, items: List[InvoiceItem]) -> List[InvoiceItem]:
        """Create multiple invoice items"""
        db.add_all(items)
        await db.flush()
        return items
