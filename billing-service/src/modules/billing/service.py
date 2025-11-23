"""
Billing Service (Business logic)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from datetime import date
from decimal import Decimal
import httpx

from src.modules.billing.models import Invoice, InvoiceItem, InvoiceType, InvoiceStatus
from src.modules.billing.repository import InvoiceRepository, InvoiceItemRepository
from src.modules.billing.schemas import (
    InvoiceCreate, InvoiceUpdateStatus,
    InvoiceResponse, InvoiceDetailResponse, InvoiceListResponse,
    InvoiceItemResponse, InvoiceStats
)

# URLs of other services (should be in config)
ORDER_SERVICE_URL = "http://order-service:8003"
PATIENT_SERVICE_URL = "http://patient-service:8002"


class InvoiceService:
    """Business logic for Invoice operations"""

    @staticmethod
    async def get_all_invoices(
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
    ) -> InvoiceListResponse:
        """Get all invoices with filters and pagination"""
        invoices, total = await InvoiceRepository.get_all(
            db, page, page_size, search, invoice_type, invoice_status,
            patient_id, location_id, date_from, date_to
        )

        invoice_responses = [InvoiceResponse.model_validate(inv) for inv in invoices]

        return InvoiceListResponse(
            total=total,
            page=page,
            page_size=page_size,
            invoices=invoice_responses
        )

    @staticmethod
    async def get_invoice_by_id(db: AsyncSession, invoice_id: int) -> InvoiceDetailResponse:
        """Get invoice by ID with items"""
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante con ID {invoice_id} no encontrado"
            )

        # Convert to response
        invoice_dict = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "order_id": invoice.order_id,
            "patient_id": invoice.patient_id,
            "location_id": invoice.location_id,
            "invoice_type": invoice.invoice_type,
            "invoice_status": invoice.invoice_status,
            "customer_document_type": invoice.customer_document_type,
            "customer_document_number": invoice.customer_document_number,
            "customer_name": invoice.customer_name,
            "customer_address": invoice.customer_address,
            "subtotal": invoice.subtotal,
            "tax": invoice.tax,
            "total": invoice.total,
            "issue_date": invoice.issue_date,
            "created_at": invoice.created_at,
            "items": [InvoiceItemResponse.model_validate(item) for item in invoice.items]
        }
        return InvoiceDetailResponse(**invoice_dict)

    @staticmethod
    async def get_invoice_by_order(db: AsyncSession, order_id: int) -> InvoiceDetailResponse:
        """Get invoice by order ID"""
        invoice = await InvoiceRepository.get_by_order_id(db, order_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró comprobante para la orden {order_id}"
            )

        # Reload with items
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice.id)

        invoice_dict = {
            "id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "order_id": invoice.order_id,
            "patient_id": invoice.patient_id,
            "location_id": invoice.location_id,
            "invoice_type": invoice.invoice_type,
            "invoice_status": invoice.invoice_status,
            "customer_document_type": invoice.customer_document_type,
            "customer_document_number": invoice.customer_document_number,
            "customer_name": invoice.customer_name,
            "customer_address": invoice.customer_address,
            "subtotal": invoice.subtotal,
            "tax": invoice.tax,
            "total": invoice.total,
            "issue_date": invoice.issue_date,
            "created_at": invoice.created_at,
            "items": [InvoiceItemResponse.model_validate(item) for item in invoice.items]
        }
        return InvoiceDetailResponse(**invoice_dict)

    @staticmethod
    async def create_invoice_from_order(
        db: AsyncSession,
        data: InvoiceCreate
    ) -> InvoiceDetailResponse:
        """Create invoice from an order"""
        # Check if invoice already exists for this order
        existing = await InvoiceRepository.get_by_order_id(db, data.order_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un comprobante para la orden {data.order_id}"
            )

        # Fetch order data from order-service
        async with httpx.AsyncClient() as client:
            try:
                order_response = await client.get(
                    f"{ORDER_SERVICE_URL}/api/v1/orders/{data.order_id}",
                    timeout=10.0
                )
                if order_response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Orden {data.order_id} no encontrada"
                    )
                order_response.raise_for_status()
                order_data = order_response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error al comunicarse con order-service: {str(e)}"
                )

        # Fetch patient data from patient-service
        patient_id = order_data["patient_id"]
        async with httpx.AsyncClient() as client:
            try:
                patient_response = await client.get(
                    f"{PATIENT_SERVICE_URL}/api/v1/patients/{patient_id}",
                    timeout=10.0
                )
                if patient_response.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Paciente {patient_id} no encontrado"
                    )
                patient_response.raise_for_status()
                patient_data = patient_response.json()
            except httpx.HTTPError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Error al comunicarse con patient-service: {str(e)}"
                )

        # Validate invoice type matches document type
        if data.invoice_type == InvoiceType.FACTURA and patient_data["document_type"] != "RUC":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las facturas solo se pueden emitir para clientes con RUC"
            )

        # Prepare customer data
        if patient_data["document_type"] == "RUC":
            customer_name = patient_data["business_name"]
        else:
            customer_name = f"{patient_data['first_name']} {patient_data['last_name']}"

        # Calculate totals (no tax for now, can be added later)
        subtotal = Decimal(str(order_data["total"]))
        tax = Decimal("0.00")
        total = subtotal + tax

        # Generate invoice number
        invoice_number = await InvoiceRepository.generate_invoice_number(db, data.invoice_type)

        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            order_id=data.order_id,
            patient_id=patient_id,
            location_id=order_data["location_id"],
            invoice_type=data.invoice_type,
            invoice_status=InvoiceStatus.PENDING,
            customer_document_type=patient_data["document_type"],
            customer_document_number=patient_data["document_number"],
            customer_name=customer_name,
            customer_address=patient_data.get("address"),
            subtotal=subtotal,
            tax=tax,
            total=total
        )
        invoice = await InvoiceRepository.create(db, invoice)

        # Create invoice items from order items
        invoice_items = []
        for order_item in order_data["items"]:
            item = InvoiceItem(
                invoice_id=invoice.id,
                service_name=order_item["service_name"],
                quantity=order_item["quantity"],
                unit_price=Decimal(str(order_item["unit_price"])),
                subtotal=Decimal(str(order_item["subtotal"]))
            )
            invoice_items.append(item)

        await InvoiceItemRepository.create_many(db, invoice_items)
        await db.commit()

        # Reload invoice with items
        return await InvoiceService.get_invoice_by_id(db, invoice.id)

    @staticmethod
    async def update_invoice_status(
        db: AsyncSession,
        invoice_id: int,
        data: InvoiceUpdateStatus
    ) -> InvoiceResponse:
        """Update invoice status"""
        invoice = await InvoiceRepository.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante con ID {invoice_id} no encontrado"
            )

        # Validate status transitions
        if invoice.invoice_status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede cambiar el estado de un comprobante anulado"
            )

        invoice.invoice_status = data.invoice_status
        invoice = await InvoiceRepository.update(db, invoice)
        return InvoiceResponse.model_validate(invoice)

    @staticmethod
    async def cancel_invoice(db: AsyncSession, invoice_id: int) -> InvoiceResponse:
        """Cancel invoice"""
        invoice = await InvoiceRepository.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante con ID {invoice_id} no encontrado"
            )

        if invoice.invoice_status == InvoiceStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El comprobante ya está anulado"
            )

        invoice.invoice_status = InvoiceStatus.CANCELLED
        invoice = await InvoiceRepository.update(db, invoice)
        return InvoiceResponse.model_validate(invoice)

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> InvoiceStats:
        """Get invoice statistics"""
        stats = await InvoiceRepository.get_statistics(db, date_from, date_to)
        return InvoiceStats(**stats)
