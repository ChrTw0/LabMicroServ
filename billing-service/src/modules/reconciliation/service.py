"""
Reconciliation Service (Business logic for daily closures and reconciliation)
"""
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import date
from decimal import Decimal

from src.modules.reconciliation.models import DailyClosure, Discrepancy, ClosureStatus
from src.modules.reconciliation.repository import DailyClosureRepository, DiscrepancyRepository
from src.modules.reconciliation.schemas import (
    DailyClosureCreate, DailyClosureResponse, DailyClosureDetailResponse,
    DailyClosureListResponse, DailyClosureReopen,
    DiscrepancyResponse, DiscrepancyCreate, DiscrepancyResolve,
    ClosureStats, ReconciliationReport, PaymentMethodSummary
)
from src.core.config import settings


class ReconciliationService:
    """Business logic for Reconciliation operations"""

    @staticmethod
    async def get_all_closures(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        location_id: Optional[int] = None,
        status: Optional[ClosureStatus] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> DailyClosureListResponse:
        """Get all closures with filters and pagination - RF-062"""
        closures, total = await DailyClosureRepository.get_all(
            db, page, page_size, location_id, status, date_from, date_to
        )

        closure_responses = [DailyClosureResponse.model_validate(c) for c in closures]

        return DailyClosureListResponse(
            total=total,
            page=page,
            page_size=page_size,
            closures=closure_responses
        )

    @staticmethod
    async def get_closure_by_id(db: AsyncSession, closure_id: int) -> DailyClosureDetailResponse:
        """Get closure by ID with discrepancies"""
        closure = await DailyClosureRepository.get_by_id_with_discrepancies(db, closure_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cierre con ID {closure_id} no encontrado"
            )

        return DailyClosureDetailResponse.model_validate(closure)

    @staticmethod
    async def create_daily_closure(
        db: AsyncSession,
        data: DailyClosureCreate
    ) -> DailyClosureDetailResponse:
        """Create a new daily closure and perform reconciliation - RF-056, RF-057, RF-058"""
        # Check if closure already exists for this location and date
        existing = await DailyClosureRepository.get_by_location_and_date(
            db, data.location_id, data.closure_date
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un cierre para la sede {data.location_id} en la fecha {data.closure_date}"
            )

        # Calculate expected total from orders and invoices
        expected_total = await ReconciliationService._calculate_expected_total(
            db, data.location_id, data.closure_date
        )

        # Calculate difference
        difference = data.registered_total - expected_total

        # Create closure
        closure = DailyClosure(
            location_id=data.location_id,
            closure_date=data.closure_date,
            status=ClosureStatus.OPEN,
            expected_total=expected_total,
            registered_total=data.registered_total,
            difference=difference
        )
        closure = await DailyClosureRepository.create(db, closure)

        # Detect discrepancies (RF-058)
        discrepancies = []
        if abs(difference) > Decimal("0.01"):  # Tolerance of 0.01
            desc = f"Diferencia de S/ {difference:.2f} entre el total esperado (S/ {expected_total:.2f}) y el total registrado (S/ {data.registered_total:.2f})"
            discrepancy = Discrepancy(
                closure_id=closure.id,
                description=desc,
                is_resolved=False
            )
            discrepancies.append(discrepancy)

        # Check payment methods reconciliation
        payment_discrepancies = await ReconciliationService._check_payment_methods(
            db, data.location_id, data.closure_date
        )
        for desc in payment_discrepancies:
            discrepancy = Discrepancy(
                closure_id=closure.id,
                description=desc,
                is_resolved=False
            )
            discrepancies.append(discrepancy)

        if discrepancies:
            await DiscrepancyRepository.create_many(db, discrepancies)
            # TODO: Send alerts to supervisor and admin (RF-061)
            # This requires notification service integration

        # Reload closure with discrepancies
        return await ReconciliationService.get_closure_by_id(db, closure.id)

    @staticmethod
    async def close_daily_closure(
        db: AsyncSession,
        closure_id: int
    ) -> DailyClosureResponse:
        """Close a daily closure (mark as CLOSED)"""
        closure = await DailyClosureRepository.get_by_id(db, closure_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cierre con ID {closure_id} no encontrado"
            )

        if closure.status == ClosureStatus.CLOSED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cierre ya está cerrado"
            )

        closure.status = ClosureStatus.CLOSED
        closure = await DailyClosureRepository.update(db, closure)

        return DailyClosureResponse.model_validate(closure)

    @staticmethod
    async def reopen_closure(
        db: AsyncSession,
        closure_id: int,
        data: DailyClosureReopen
    ) -> DailyClosureResponse:
        """Reopen a closed closure - RF-063 (only admin)"""
        closure = await DailyClosureRepository.get_by_id(db, closure_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cierre con ID {closure_id} no encontrado"
            )

        if closure.status == ClosureStatus.OPEN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El cierre ya está abierto"
            )

        # Log reason (could be saved to a separate audit table)
        # For now, we just reopen it
        closure.status = ClosureStatus.OPEN
        closure = await DailyClosureRepository.update(db, closure)

        # TODO: Register the reason in an audit log
        # TODO: Send notification to admin about reopening

        return DailyClosureResponse.model_validate(closure)

    @staticmethod
    async def add_discrepancy(
        db: AsyncSession,
        closure_id: int,
        data: DiscrepancyCreate
    ) -> DiscrepancyResponse:
        """Add a manual discrepancy to a closure"""
        closure = await DailyClosureRepository.get_by_id(db, closure_id)
        if not closure:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cierre con ID {closure_id} no encontrado"
            )

        discrepancy = Discrepancy(
            closure_id=closure_id,
            description=data.description,
            is_resolved=False
        )
        discrepancy = await DiscrepancyRepository.create(db, discrepancy)

        return DiscrepancyResponse.model_validate(discrepancy)

    @staticmethod
    async def resolve_discrepancy(
        db: AsyncSession,
        discrepancy_id: int,
        data: DiscrepancyResolve
    ) -> DiscrepancyResponse:
        """Mark a discrepancy as resolved"""
        discrepancy = await DiscrepancyRepository.get_by_id(db, discrepancy_id)
        if not discrepancy:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discrepancia con ID {discrepancy_id} no encontrada"
            )

        discrepancy.is_resolved = data.is_resolved
        discrepancy = await DiscrepancyRepository.update(db, discrepancy)

        return DiscrepancyResponse.model_validate(discrepancy)

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> ClosureStats:
        """Get closure statistics"""
        stats = await DailyClosureRepository.get_statistics(db, date_from, date_to)
        return ClosureStats(**stats)

    @staticmethod
    async def get_reconciliation_report(
        db: AsyncSession,
        location_id: int,
        closure_date: date
    ) -> ReconciliationReport:
        """Generate complete reconciliation report - RF-057, RF-059"""
        # Get orders from order-service
        async with httpx.AsyncClient() as client:
            try:
                orders_resp = await client.get(
                    f"{settings.order_service_url}/api/v1/orders",
                    params={
                        "location_id": location_id,
                        "date_from": closure_date,
                        "date_to": closure_date,
                        "page_size": 1000
                    },
                    timeout=10.0
                )
                if orders_resp.status_code == 200:
                    orders_data = orders_resp.json()
                    total_orders = orders_data.get("total", 0)
                    orders = orders_data.get("orders", [])
                else:
                    total_orders = 0
                    orders = []
            except Exception:
                total_orders = 0
                orders = []

        # Get invoices from local database
        from src.modules.billing.repository import InvoiceRepository
        from src.modules.billing.models import InvoiceStatus, Invoice
        from sqlalchemy import select, func, and_

        invoice_query = select(func.count()).select_from(Invoice).where(
            and_(
                Invoice.location_id == location_id,
                func.date(Invoice.issue_date) == closure_date,
                Invoice.invoice_status != InvoiceStatus.CANCELLED
            )
        )
        total_invoices = (await db.execute(invoice_query)).scalar() or 0

        # Calculate total payments from orders
        total_payments = Decimal("0.00")
        for order in orders:
            # Sum all payments for each order
            payments = order.get("payments", [])
            for payment in payments:
                total_payments += Decimal(str(payment.get("amount", 0)))

        # Calculate total billed from invoices
        from src.modules.billing.models import Invoice
        billed_query = select(func.sum(Invoice.total)).where(
            and_(
                Invoice.location_id == location_id,
                func.date(Invoice.issue_date) == closure_date,
                Invoice.invoice_status != InvoiceStatus.CANCELLED
            )
        )
        total_billed = (await db.execute(billed_query)).scalar() or Decimal("0.00")

        # Get payment method summary (RF-059, RF-060)
        payment_methods = await ReconciliationService._get_payment_method_summary(
            db, location_id, closure_date
        )

        # Get discrepancies if closure exists
        closure = await DailyClosureRepository.get_by_location_and_date(
            db, location_id, closure_date
        )
        if closure:
            discrepancies_list = await DiscrepancyRepository.get_by_closure(db, closure.id)
            discrepancies = [DiscrepancyResponse.model_validate(d) for d in discrepancies_list]
            has_discrepancies = len(discrepancies) > 0
        else:
            discrepancies = []
            has_discrepancies = False

        return ReconciliationReport(
            closure_date=closure_date,
            location_id=location_id,
            total_orders=total_orders,
            total_invoices=total_invoices,
            total_payments=total_payments,
            total_billed=total_billed,
            payment_methods=payment_methods,
            discrepancies=discrepancies,
            has_discrepancies=has_discrepancies
        )

    # ==================== HELPER METHODS ====================

    @staticmethod
    async def _calculate_expected_total(
        db: AsyncSession,
        location_id: int,
        closure_date: date
    ) -> Decimal:
        """Calculate expected total from system (orders + payments)"""
        # Query orders from order-service
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{settings.order_service_url}/api/v1/orders",
                    params={
                        "location_id": location_id,
                        "date_from": closure_date,
                        "date_to": closure_date,
                        "page_size": 1000
                    },
                    timeout=10.0
                )
                if resp.status_code == 200:
                    data = resp.json()
                    orders = data.get("orders", [])
                    total = sum(Decimal(str(order.get("total", 0))) for order in orders)
                    return total
                else:
                    return Decimal("0.00")
            except Exception:
                return Decimal("0.00")

    @staticmethod
    async def _check_payment_methods(
        db: AsyncSession,
        location_id: int,
        closure_date: date
    ) -> List[str]:
        """Check for discrepancies in payment methods"""
        discrepancies = []

        # Get payment method summary
        payment_methods = await ReconciliationService._get_payment_method_summary(
            db, location_id, closure_date
        )

        # Check each payment method for significant differences
        for pm in payment_methods:
            if abs(pm.difference) > Decimal("0.01"):
                desc = f"Diferencia en {pm.payment_method}: esperado S/ {pm.expected_total:.2f}, registrado S/ {pm.registered_total:.2f}"
                discrepancies.append(desc)

        return discrepancies

    @staticmethod
    async def _get_payment_method_summary(
        db: AsyncSession,
        location_id: int,
        closure_date: date
    ) -> List[PaymentMethodSummary]:
        """Get payment method summary for reconciliation - RF-059"""
        # This is a simplified version
        # In a real system, you'd query actual payment records
        # For now, we return a placeholder

        # TODO: Implement actual payment method reconciliation
        # This requires querying order-service for payment details

        return [
            PaymentMethodSummary(
                payment_method="EFECTIVO",
                expected_total=Decimal("0.00"),
                registered_total=Decimal("0.00"),
                difference=Decimal("0.00")
            ),
            PaymentMethodSummary(
                payment_method="TARJETA",
                expected_total=Decimal("0.00"),
                registered_total=Decimal("0.00"),
                difference=Decimal("0.00")
            ),
            PaymentMethodSummary(
                payment_method="TRANSFERENCIA",
                expected_total=Decimal("0.00"),
                registered_total=Decimal("0.00"),
                difference=Decimal("0.00")
            ),
            PaymentMethodSummary(
                payment_method="YAPE_PLIN",
                expected_total=Decimal("0.00"),
                registered_total=Decimal("0.00"),
                difference=Decimal("0.00")
            )
        ]
