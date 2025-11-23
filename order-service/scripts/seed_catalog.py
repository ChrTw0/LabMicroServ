"""
Seed data for catalog (categories and services)
"""
import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from src.core.database import async_session_maker
from src.modules.catalog.models import Category, Service
from src.modules.catalog.repository import CategoryRepository, ServiceRepository


async def seed_catalog():
    """Seed catalog with initial categories and services"""
    async with async_session_maker() as session:
        print("🌱 Seeding catalog data...")

        # Check if categories already exist
        existing_categories = await CategoryRepository.get_all(session)
        if existing_categories:
            print(f"⚠️  Categories already exist ({len(existing_categories)} found). Skipping seed.")
            return

        # Create categories
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

        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            category = await CategoryRepository.create(session, category)
            categories.append(category)
            print(f"✅ Created category: {category.name}")

        # Create services for each category
        services_data = [
            # Análisis Clínicos
            {"name": "Hemograma Completo", "description": "Recuento completo de células sanguíneas", "category_id": categories[0].id, "current_price": Decimal("25.00")},
            {"name": "Examen de Orina Completo", "description": "Análisis físico, químico y microscópico de orina", "category_id": categories[0].id, "current_price": Decimal("15.00")},
            {"name": "Grupo Sanguíneo y Factor Rh", "description": "Determinación de tipo de sangre", "category_id": categories[0].id, "current_price": Decimal("20.00")},

            # Hematología
            {"name": "Recuento de Plaquetas", "description": "Conteo de plaquetas en sangre", "category_id": categories[1].id, "current_price": Decimal("18.00")},
            {"name": "Tiempo de Coagulación", "description": "Medición del tiempo de coagulación sanguínea", "category_id": categories[1].id, "current_price": Decimal("15.00")},
            {"name": "Velocidad de Sedimentación Globular (VSG)", "description": "Indicador de inflamación", "category_id": categories[1].id, "current_price": Decimal("12.00")},

            # Bioquímica
            {"name": "Glucosa en Ayunas", "description": "Medición de glucosa sanguínea", "category_id": categories[2].id, "current_price": Decimal("10.00")},
            {"name": "Colesterol Total", "description": "Medición de colesterol en sangre", "category_id": categories[2].id, "current_price": Decimal("15.00")},
            {"name": "Triglicéridos", "description": "Medición de triglicéridos en sangre", "category_id": categories[2].id, "current_price": Decimal("15.00")},
            {"name": "Creatinina", "description": "Evaluación de función renal", "category_id": categories[2].id, "current_price": Decimal("18.00")},
            {"name": "Urea", "description": "Evaluación de función renal", "category_id": categories[2].id, "current_price": Decimal("16.00")},
            {"name": "Ácido Úrico", "description": "Detección de gota y problemas renales", "category_id": categories[2].id, "current_price": Decimal("18.00")},
            {"name": "Transaminasas (TGO/TGP)", "description": "Evaluación de función hepática", "category_id": categories[2].id, "current_price": Decimal("30.00")},

            # Inmunología
            {"name": "Proteína C Reactiva (PCR)", "description": "Marcador de inflamación", "category_id": categories[3].id, "current_price": Decimal("25.00")},
            {"name": "Factor Reumatoide", "description": "Detección de artritis reumatoide", "category_id": categories[3].id, "current_price": Decimal("35.00")},
            {"name": "Antiestreptolisinas O (ASLO)", "description": "Detección de infecciones estreptocócicas", "category_id": categories[3].id, "current_price": Decimal("30.00")},

            # Microbiología
            {"name": "Urocultivo", "description": "Cultivo de orina para detectar infecciones", "category_id": categories[4].id, "current_price": Decimal("40.00")},
            {"name": "Coprocultivo", "description": "Cultivo de heces para detectar bacterias", "category_id": categories[4].id, "current_price": Decimal("45.00")},
            {"name": "Antibiograma", "description": "Prueba de sensibilidad a antibióticos", "category_id": categories[4].id, "current_price": Decimal("35.00")},

            # Parasitología
            {"name": "Examen Parasitológico de Heces", "description": "Detección de parásitos intestinales", "category_id": categories[5].id, "current_price": Decimal("20.00")},
            {"name": "Test de Graham", "description": "Detección de oxiuros", "category_id": categories[5].id, "current_price": Decimal("18.00")},

            # Hormonas
            {"name": "TSH (Hormona Estimulante de Tiroides)", "description": "Evaluación de función tiroidea", "category_id": categories[6].id, "current_price": Decimal("40.00")},
            {"name": "T3 y T4", "description": "Hormonas tiroideas", "category_id": categories[6].id, "current_price": Decimal("50.00")},
            {"name": "Beta HCG (Prueba de Embarazo)", "description": "Detección de embarazo", "category_id": categories[6].id, "current_price": Decimal("30.00")},
            {"name": "Testosterona", "description": "Medición de hormona masculina", "category_id": categories[6].id, "current_price": Decimal("45.00")},

            # Perfiles
            {"name": "Perfil Lipídico Completo", "description": "Colesterol total, HDL, LDL, triglicéridos", "category_id": categories[7].id, "current_price": Decimal("45.00")},
            {"name": "Perfil Hepático", "description": "TGO, TGP, bilirrubinas, fosfatasa alcalina", "category_id": categories[7].id, "current_price": Decimal("60.00")},
            {"name": "Perfil Renal", "description": "Urea, creatinina, ácido úrico, electrolitos", "category_id": categories[7].id, "current_price": Decimal("55.00")},
            {"name": "Perfil Tiroideo", "description": "TSH, T3, T4", "category_id": categories[7].id, "current_price": Decimal("80.00")},
            {"name": "Chequeo Preventivo Básico", "description": "Hemograma, glucosa, colesterol, triglicéridos, orina", "category_id": categories[7].id, "current_price": Decimal("75.00")},
        ]

        for svc_data in services_data:
            service = Service(**svc_data)
            service = await ServiceRepository.create(session, service)
            print(f"✅ Created service: {service.name} - S/ {service.current_price}")

        print(f"\n🎉 Seed completed successfully!")
        print(f"   - {len(categories)} categories created")
        print(f"   - {len(services_data)} services created")


if __name__ == "__main__":
    asyncio.run(seed_catalog())
