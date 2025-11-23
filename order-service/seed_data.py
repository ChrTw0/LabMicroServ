"""
Seed script to populate initial data for order-service

This script creates:
- Default categories (8 categories)
- Sample services (~30 services)
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

from src.core.config import settings
from src.modules.catalog.models import Category, Service
from src.modules.orders.models import Order, OrderItem, OrderPayment, OrderStatus, PaymentMethod

# Configure logger
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>"
)


async def create_categories(session: AsyncSession) -> dict[str, Category]:
    """Create default categories"""
    logger.info("Creating default categories...")

    categories_data = [
        {"name": "Análisis Clínicos", "is_active": True},
        {"name": "Hematología", "is_active": True},
        {"name": "Bioquímica", "is_active": True},
        {"name": "Inmunología", "is_active": True},
        {"name": "Microbiología", "is_active": True},
        {"name": "Parasitología", "is_active": True},
        {"name": "Hormonas", "is_active": True},
        {"name": "Perfiles", "is_active": True},
    ]

    created_categories = {}

    for cat_data in categories_data:
        # Check if category already exists
        result = await session.execute(
            select(Category).where(Category.name == cat_data["name"])
        )
        existing_cat = result.scalar_one_or_none()

        if existing_cat:
            logger.info(f"Category '{cat_data['name']}' already exists, skipping...")
            created_categories[cat_data["name"]] = existing_cat
        else:
            category = Category(**cat_data)
            session.add(category)
            await session.flush()
            await session.refresh(category)
            created_categories[cat_data["name"]] = category
            logger.success(f"Created category: {cat_data['name']} (ID: {category.id})")

    await session.commit()
    return created_categories


async def create_services(session: AsyncSession, categories: dict[str, Category]) -> int:
    """Create sample services"""
    logger.info("Creating sample services...")

    services_data = [
        # Análisis Clínicos
        {"name": "Hemograma Completo", "description": "Recuento completo de células sanguíneas", "category": "Análisis Clínicos", "price": "25.00"},
        {"name": "Examen de Orina Completo", "description": "Análisis físico, químico y microscópico de orina", "category": "Análisis Clínicos", "price": "15.00"},
        {"name": "Grupo Sanguíneo y Factor Rh", "description": "Determinación de tipo de sangre", "category": "Análisis Clínicos", "price": "20.00"},

        # Hematología
        {"name": "Recuento de Plaquetas", "description": "Conteo de plaquetas en sangre", "category": "Hematología", "price": "18.00"},
        {"name": "Tiempo de Coagulación", "description": "Medición del tiempo de coagulación sanguínea", "category": "Hematología", "price": "15.00"},
        {"name": "Velocidad de Sedimentación Globular (VSG)", "description": "Indicador de inflamación", "category": "Hematología", "price": "12.00"},

        # Bioquímica
        {"name": "Glucosa en Ayunas", "description": "Medición de glucosa sanguínea", "category": "Bioquímica", "price": "10.00"},
        {"name": "Colesterol Total", "description": "Medición de colesterol en sangre", "category": "Bioquímica", "price": "15.00"},
        {"name": "Triglicéridos", "description": "Medición de triglicéridos en sangre", "category": "Bioquímica", "price": "15.00"},
        {"name": "Creatinina", "description": "Evaluación de función renal", "category": "Bioquímica", "price": "18.00"},
        {"name": "Urea", "description": "Evaluación de función renal", "category": "Bioquímica", "price": "16.00"},
        {"name": "Ácido Úrico", "description": "Detección de gota y problemas renales", "category": "Bioquímica", "price": "18.00"},
        {"name": "Transaminasas (TGO/TGP)", "description": "Evaluación de función hepática", "category": "Bioquímica", "price": "30.00"},

        # Inmunología
        {"name": "Proteína C Reactiva (PCR)", "description": "Marcador de inflamación", "category": "Inmunología", "price": "25.00"},
        {"name": "Factor Reumatoide", "description": "Detección de artritis reumatoide", "category": "Inmunología", "price": "35.00"},
        {"name": "Antiestreptolisinas O (ASLO)", "description": "Detección de infecciones estreptocócicas", "category": "Inmunología", "price": "30.00"},

        # Microbiología
        {"name": "Urocultivo", "description": "Cultivo de orina para detectar infecciones", "category": "Microbiología", "price": "40.00"},
        {"name": "Coprocultivo", "description": "Cultivo de heces para detectar bacterias", "category": "Microbiología", "price": "45.00"},
        {"name": "Antibiograma", "description": "Prueba de sensibilidad a antibióticos", "category": "Microbiología", "price": "35.00"},

        # Parasitología
        {"name": "Examen Parasitológico de Heces", "description": "Detección de parásitos intestinales", "category": "Parasitología", "price": "20.00"},
        {"name": "Test de Graham", "description": "Detección de oxiuros", "category": "Parasitología", "price": "18.00"},

        # Hormonas
        {"name": "TSH (Hormona Estimulante de Tiroides)", "description": "Evaluación de función tiroidea", "category": "Hormonas", "price": "40.00"},
        {"name": "T3 y T4", "description": "Hormonas tiroideas", "category": "Hormonas", "price": "50.00"},
        {"name": "Beta HCG (Prueba de Embarazo)", "description": "Detección de embarazo", "category": "Hormonas", "price": "30.00"},
        {"name": "Testosterona", "description": "Medición de hormona masculina", "category": "Hormonas", "price": "45.00"},

        # Perfiles
        {"name": "Perfil Lipídico Completo", "description": "Colesterol total, HDL, LDL, triglicéridos", "category": "Perfiles", "price": "45.00"},
        {"name": "Perfil Hepático", "description": "TGO, TGP, bilirrubinas, fosfatasa alcalina", "category": "Perfiles", "price": "60.00"},
        {"name": "Perfil Renal", "description": "Urea, creatinina, ácido úrico, electrolitos", "category": "Perfiles", "price": "55.00"},
        {"name": "Perfil Tiroideo", "description": "TSH, T3, T4", "category": "Perfiles", "price": "80.00"},
        {"name": "Chequeo Preventivo Básico", "description": "Hemograma, glucosa, colesterol, triglicéridos, orina", "category": "Perfiles", "price": "75.00"},
    ]

    created_count = 0

    for svc_data in services_data:
        # Check if service already exists
        result = await session.execute(
            select(Service).where(Service.name == svc_data["name"])
        )
        existing_svc = result.scalar_one_or_none()

        if existing_svc:
            logger.info(f"Service '{svc_data['name']}' already exists, skipping...")
        else:
            category = categories[svc_data["category"]]
            service = Service(
                name=svc_data["name"],
                description=svc_data["description"],
                category_id=category.id,
                current_price=Decimal(svc_data["price"]),
                is_active=True
            )
            session.add(service)
            created_count += 1
            logger.success(f"Created service: {svc_data['name']} - S/ {svc_data['price']}")

    await session.commit()
    return created_count


async def create_orders(session: AsyncSession) -> int:
    """Create sample orders"""
    logger.info("Creating sample orders...")

    # Check if orders already exist
    result = await session.execute(select(Order))
    existing_orders = result.scalars().all()
    if existing_orders:
        logger.info(f"Orders already exist ({len(existing_orders)} found). Skipping seed.")
        return 0

    # Get some services
    result = await session.execute(select(Service).limit(10))
    services = list(result.scalars().all())

    if not services:
        logger.warning("No services found. Cannot create orders.")
        return 0

    from datetime import datetime, timedelta

    # Sample orders data
    orders_data = [
        {
            "order_number": f"ORD-{datetime.now().strftime('%Y%m%d')}-0001",
            "patient_id": 1,  # Juan Pérez (assuming patient-service seed was run)
            "location_id": 1,
            "status": OrderStatus.COMPLETADA,
            "items": [
                {"service": services[0], "quantity": 1},
                {"service": services[1], "quantity": 1},
            ],
            "payments": [
                {"method": PaymentMethod.EFECTIVO, "amount": Decimal("40.00")}
            ],
            "created_days_ago": 5
        },
        {
            "order_number": f"ORD-{datetime.now().strftime('%Y%m%d')}-0002",
            "patient_id": 2,  # María González
            "location_id": 1,
            "status": OrderStatus.COMPLETADA,
            "items": [
                {"service": services[2], "quantity": 1},
                {"service": services[6], "quantity": 1},
            ],
            "payments": [
                {"method": PaymentMethod.YAPE_PLIN, "amount": Decimal("30.00")}
            ],
            "created_days_ago": 3
        },
        {
            "order_number": f"ORD-{datetime.now().strftime('%Y%m%d')}-0003",
            "patient_id": 3,  # Carlos Rodríguez
            "location_id": 1,
            "status": OrderStatus.EN_PROCESO,
            "items": [
                {"service": services[7], "quantity": 1},
                {"service": services[8], "quantity": 1},
                {"service": services[9], "quantity": 1},
            ],
            "payments": [
                {"method": PaymentMethod.TARJETA, "amount": Decimal("20.00")},
                {"method": PaymentMethod.EFECTIVO, "amount": Decimal("20.00")}
            ],
            "created_days_ago": 1
        },
        {
            "order_number": f"ORD-{datetime.now().strftime('%Y%m%d')}-0004",
            "patient_id": 4,  # Ana Martínez
            "location_id": 2,
            "status": OrderStatus.REGISTRADA,
            "items": [
                {"service": services[3], "quantity": 1},
            ],
            "payments": [],
            "created_days_ago": 0
        },
    ]

    created_count = 0

    for order_data in orders_data:
        # Calculate total
        total = sum(item["service"].current_price * item["quantity"] for item in order_data["items"])

        # Create order
        created_at = datetime.now() - timedelta(days=order_data["created_days_ago"])
        order = Order(
            order_number=order_data["order_number"],
            patient_id=order_data["patient_id"],
            location_id=order_data["location_id"],
            status=order_data["status"],
            total=total,
            created_at=created_at
        )
        session.add(order)
        await session.flush()
        await session.refresh(order)

        # Create order items
        for item_data in order_data["items"]:
            service = item_data["service"]
            quantity = item_data["quantity"]
            subtotal = service.current_price * quantity

            order_item = OrderItem(
                order_id=order.id,
                service_id=service.id,
                service_name=service.name,
                unit_price=service.current_price,
                quantity=quantity,
                subtotal=subtotal
            )
            session.add(order_item)

        # Create payments
        for payment_data in order_data["payments"]:
            payment = OrderPayment(
                order_id=order.id,
                payment_method=payment_data["method"],
                amount=payment_data["amount"]
            )
            session.add(payment)

        created_count += 1
        logger.success(f"Created order: {order.order_number} - S/ {order.total} ({order.status.value})")

    await session.commit()
    return created_count


async def seed_database():
    """Main seed function"""
    logger.info("=" * 60)
    logger.info("Starting database seeding for order-service")
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
            # Create categories
            categories = await create_categories(session)

            # Create services
            services_count = await create_services(session, categories)

            # Create orders
            orders_count = await create_orders(session)

            logger.info("=" * 60)
            logger.success("Database seeding completed successfully!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("📋 Summary:")
            logger.info(f"  - Categories created: {len(categories)}")
            logger.info(f"  - Services created: {services_count}")
            logger.info(f"  - Orders created: {orders_count}")
            logger.info("")
            logger.info("🔍 You can now explore the data:")
            logger.info("  Categories: GET http://localhost:8003/api/v1/categories")
            logger.info("  Services:   GET http://localhost:8003/api/v1/services")
            logger.info("  Orders:     GET http://localhost:8003/api/v1/orders")
            logger.info("  API Docs:   http://localhost:8003/docs")
            logger.info("")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
