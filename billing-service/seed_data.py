"""
Seed script to populate initial data for billing-service

This script creates:
- Sample invoices (Boletas y Facturas)
"""
import asyncio
import sys
from pathlib import Path
from decimal import Decimal

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from loguru import logger
from datetime import datetime, timedelta

from src.core.config import settings
from src.modules.billing.models import Invoice, InvoiceItem, InvoiceType, InvoiceStatus

# Configure logger
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)


async def create_invoices(session: AsyncSession) -> int:
    """Create sample invoices"""
    logger.info("Creating sample invoices...")

    # Check if invoices already exist
    result = await session.execute(select(Invoice))
    existing_invoices = result.scalars().all()
    if existing_invoices:
        logger.info(f"Invoices already exist ({len(existing_invoices)} found). Skipping seed.")
        return 0

    # Sample invoices data
    invoices_data = [
        {
            "invoice_number": "B001-00000001",
            "order_id": 1,  # Assuming order-service seed was run
            "patient_id": 1,  # Juan Pérez
            "location_id": 1,
            "invoice_type": InvoiceType.BOLETA,
            "invoice_status": InvoiceStatus.ACCEPTED,
            "customer_document_type": "DNI",
            "customer_document_number": "12345678",
            "customer_name": "Juan Pérez García",
            "customer_address": "Av. Los Álamos 123, Lima",
            "subtotal": Decimal("40.00"),
            "tax": Decimal("0.00"),
            "total": Decimal("40.00"),
            "items": [
                {"service_name": "Hemograma Completo", "quantity": 1, "unit_price": Decimal("25.00"), "subtotal": Decimal("25.00")},
                {"service_name": "Examen de Orina Completo", "quantity": 1, "unit_price": Decimal("15.00"), "subtotal": Decimal("15.00")},
            ],
            "created_days_ago": 5
        },
        {
            "invoice_number": "B001-00000002",
            "order_id": 2,
            "patient_id": 2,  # María González
            "location_id": 1,
            "invoice_type": InvoiceType.BOLETA,
            "invoice_status": InvoiceStatus.ACCEPTED,
            "customer_document_type": "DNI",
            "customer_document_number": "87654321",
            "customer_name": "María González López",
            "customer_address": "Jr. Las Flores 456, Lima",
            "subtotal": Decimal("30.00"),
            "tax": Decimal("0.00"),
            "total": Decimal("30.00"),
            "items": [
                {"service_name": "Grupo Sanguíneo y Factor Rh", "quantity": 1, "unit_price": Decimal("20.00"), "subtotal": Decimal("20.00")},
                {"service_name": "Glucosa en Ayunas", "quantity": 1, "unit_price": Decimal("10.00"), "subtotal": Decimal("10.00")},
            ],
            "created_days_ago": 3
        },
        {
            "invoice_number": "F001-00000001",
            "order_id": 5,  # Assuming corporate order exists
            "patient_id": 6,  # Laboratorios Médicos S.A.C.
            "location_id": 1,
            "invoice_type": InvoiceType.FACTURA,
            "invoice_status": InvoiceStatus.ACCEPTED,
            "customer_document_type": "RUC",
            "customer_document_number": "20123456789",
            "customer_name": "Laboratorios Médicos S.A.C.",
            "customer_address": "Av. Javier Prado 1234, San Isidro",
            "subtotal": Decimal("150.00"),
            "tax": Decimal("27.00"),  # 18% IGV
            "total": Decimal("177.00"),
            "items": [
                {"service_name": "Perfil Hepático", "quantity": 1, "unit_price": Decimal("60.00"), "subtotal": Decimal("60.00")},
                {"service_name": "Perfil Renal", "quantity": 1, "unit_price": Decimal("55.00"), "subtotal": Decimal("55.00")},
                {"service_name": "Hemograma Completo", "quantity": 1, "unit_price": Decimal("25.00"), "subtotal": Decimal("25.00")},
                {"service_name": "Glucosa en Ayunas", "quantity": 1, "unit_price": Decimal("10.00"), "subtotal": Decimal("10.00")},
            ],
            "created_days_ago": 2
        },
    ]

    created_count = 0

    for invoice_data in invoices_data:
        # Create invoice
        items = invoice_data.pop("items")
        created_days_ago = invoice_data.pop("created_days_ago")

        issue_date = datetime.now() - timedelta(days=created_days_ago)
        invoice_data["issue_date"] = issue_date
        invoice_data["created_at"] = issue_date

        invoice = Invoice(**invoice_data)
        session.add(invoice)
        await session.flush()
        await session.refresh(invoice)

        # Create invoice items
        for item_data in items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                **item_data
            )
            session.add(invoice_item)

        created_count += 1
        logger.success(f"Created invoice: {invoice.invoice_number} - S/ {invoice.total} ({invoice.invoice_type.value})")

    await session.commit()
    return created_count


async def seed_database():
    """Main seed function"""
    logger.info("=" * 60)
    logger.info("Starting database seeding for billing-service")
    logger.info("=" * 60)

    # Create async engine
    engine = create_async_engine(
        settings.database_url,
        echo=False
    )

    # Create async session
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        try:
            # Create invoices
            invoices_count = await create_invoices(session)

            logger.info("=" * 60)
            logger.success("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📋 Summary:")
            logger.info(f"  - Invoices created: {invoices_count}")
            logger.info("")
            logger.info("🔍 You can now explore the data:")
            logger.info("  Invoices:    GET http://localhost:8004/api/v1/invoices")
            logger.info("  Statistics:  GET http://localhost:8004/api/v1/invoices/statistics")
            logger.info("  API Docs:    http://localhost:8004/docs")
            logger.info("")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
