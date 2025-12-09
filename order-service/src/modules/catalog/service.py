"""
Catalog Service (Business logic)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from typing import Optional, List, Dict
from decimal import Decimal
from loguru import logger

from src.modules.catalog.models import Category, Service, PriceHistory
from src.modules.catalog.repository import CategoryRepository, ServiceRepository, PriceHistoryRepository
from src.modules.catalog.schemas import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithServicesCount,
    ServiceCreate, ServiceUpdate, ServiceResponse, ServiceListResponse,
    UpdateServicePriceRequest, PriceHistoryResponse, ServiceDetailResponse,
    PriceHistoryListResponse
)


# ==================== Category Service ====================

class CategoryService:
    """Business logic for Category operations"""

    @staticmethod
    async def get_all_categories(
        db: AsyncSession,
        active_only: bool = False
    ) -> List[CategoryResponse]:
        """Get all categories"""
        categories = await CategoryRepository.get_all(db, active_only)
        return [CategoryResponse.model_validate(cat) for cat in categories]

    @staticmethod
    async def get_all_categories_with_count(
        db: AsyncSession,
        active_only: bool = False
    ) -> List[CategoryWithServicesCount]:
        """Get all categories with service count"""
        categories_with_count = await CategoryRepository.get_all_with_services_count(db, active_only)

        result = []
        for category, count in categories_with_count:
            cat_dict = {
                "id": category.id,
                "name": category.name,
                "is_active": category.is_active,
                "services_count": count
            }
            result.append(CategoryWithServicesCount(**cat_dict))

        return result

    @staticmethod
    async def get_category_by_id(db: AsyncSession, category_id: int) -> CategoryResponse:
        """Get category by ID"""
        category = await CategoryRepository.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada"
            )
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def create_category(
        db: AsyncSession,
        data: CategoryCreate
    ) -> CategoryResponse:
        """Create a new category"""
        # Check if category name already exists
        existing = await CategoryRepository.get_by_name(db, data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe una categoría con el nombre '{data.name}'"
            )

        # Create category
        category = Category(
            name=data.name,
            is_active=data.is_active
        )
        category = await CategoryRepository.create(db, category)
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def update_category(
        db: AsyncSession,
        category_id: int,
        data: CategoryUpdate
    ) -> CategoryResponse:
        """Update category"""
        category = await CategoryRepository.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada"
            )

        # Check if new name already exists
        if data.name and data.name != category.name:
            existing = await CategoryRepository.get_by_name(db, data.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe una categoría con el nombre '{data.name}'"
                )

        # Update fields
        if data.name is not None:
            category.name = data.name
        if data.is_active is not None:
            category.is_active = data.is_active

        category = await CategoryRepository.update(db, category)
        return CategoryResponse.model_validate(category)

    @staticmethod
    async def delete_category(db: AsyncSession, category_id: int) -> Dict[str, str]:
        """Delete category"""
        category = await CategoryRepository.get_by_id(db, category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada"
            )

        # Check if category has services
        services_count = await CategoryRepository.get_services_count(db, category_id)
        if services_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede eliminar la categoría porque tiene {services_count} servicio(s) asociado(s)"
            )

        await CategoryRepository.delete(db, category)
        return {"message": f"Categoría '{category.name}' eliminada exitosamente"}


# ==================== Service Service ====================

class ServiceService:
    """Business logic for Service operations"""

    @staticmethod
    async def get_all_services(
        db: AsyncSession,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None
    ) -> ServiceListResponse:
        """Get all services with filters and pagination"""
        # Validate category exists if provided
        if category_id:
            category = await CategoryRepository.get_by_id(db, category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Categoría con ID {category_id} no encontrada"
                )

        services, total = await ServiceRepository.get_all(
            db, page, page_size, search, category_id, is_active, min_price, max_price
        )

        # Convert to response schema
        service_responses = []
        for service in services:
            category_name = "Sin categoría"
            if service.category:
                category_name = service.category.name
            else:
                logger.warning(f"El servicio con ID {service.id} tiene una categoría inválida (category_id: {service.category_id})")

            service_dict = {
                "id": service.id,
                "code": service.code,
                "name": service.name,
                "description": service.description,
                "category_id": service.category_id,
                "category_name": category_name,
                "current_price": service.current_price,
                "is_active": service.is_active
            }
            service_responses.append(ServiceResponse(**service_dict))

        return ServiceListResponse(
            total=total,
            page=page,
            page_size=page_size,
            services=service_responses
        )

    @staticmethod
    async def get_service_by_id(db: AsyncSession, service_id: int) -> ServiceDetailResponse:
        """Get service by ID with price history"""
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio con ID {service_id} no encontrado"
            )

        # Get price history
        price_history = await PriceHistoryRepository.get_by_service_id(db, service_id, limit=10)

        category_name = "Sin categoría"
        if service.category:
            category_name = service.category.name
        else:
            logger.warning(f"El servicio con ID {service.id} tiene una categoría inválida (category_id: {service.category_id})")

        # Convert to response schema
        service_dict = {
            "id": service.id,
            "code": service.code,
            "name": service.name,
            "description": service.description,
            "category_id": service.category_id,
            "category_name": category_name,
            "current_price": service.current_price,
            "is_active": service.is_active,
            "price_history": [PriceHistoryResponse.model_validate(ph) for ph in price_history]
        }
        return ServiceDetailResponse(**service_dict)

    @staticmethod
    async def create_service(
        db: AsyncSession,
        data: ServiceCreate
    ) -> ServiceResponse:
        """Create a new service"""
        # Validate category exists
        category = await CategoryRepository.get_by_id(db, data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {data.category_id} no encontrada"
            )

        # Check if service name already exists
        existing_by_name = await ServiceRepository.get_by_name(db, data.name)
        if existing_by_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un servicio con el nombre '{data.name}'"
            )
        
        # Check if service code already exists
        existing_by_code = await ServiceRepository.get_by_code(db, data.code)
        if existing_by_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un servicio con el código '{data.code}'"
            )

        # Create service
        service = Service(
            code=data.code,
            name=data.name,
            description=data.description,
            category_id=data.category_id,
            current_price=data.current_price,
            is_active=data.is_active
        )
        service = await ServiceRepository.create(db, service)

        category_name = "Sin categoría"
        if service.category:
            category_name = service.category.name
        else:
            logger.warning(f"El servicio con ID {service.id} tiene una categoría inválida (category_id: {service.category_id})")

        # Return response
        service_dict = {
            "id": service.id,
            "code": service.code,
            "name": service.name,
            "description": service.description,
            "category_id": service.category_id,
            "category_name": category_name,
            "current_price": service.current_price,
            "is_active": service.is_active
        }
        return ServiceResponse(**service_dict)

    @staticmethod
    async def update_service(
        db: AsyncSession,
        service_id: int,
        data: ServiceUpdate
    ) -> ServiceResponse:
        """Update service"""
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio con ID {service_id} no encontrado"
            )

        # Validate category if provided
        if data.category_id:
            category = await CategoryRepository.get_by_id(db, data.category_id)
            if not category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Categoría con ID {data.category_id} no encontrada"
                )

        # Check if new name already exists
        if data.name and data.name != service.name:
            existing_name = await ServiceRepository.get_by_name(db, data.name)
            if existing_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un servicio con el nombre '{data.name}'"
                )
        
        # Check if new code already exists
        if data.code and data.code != service.code:
            existing_code = await ServiceRepository.get_by_code(db, data.code)
            if existing_code:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un servicio con el código '{data.code}'"
                )

        # Update fields
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        service = await ServiceRepository.update(db, service)

        category_name = "Sin categoría"
        if service.category:
            category_name = service.category.name
        else:
            logger.warning(f"El servicio con ID {service.id} tiene una categoría inválida (category_id: {service.category_id})")

        # Return response
        service_dict = {
            "id": service.id,
            "code": service.code,
            "name": service.name,
            "description": service.description,
            "category_id": service.category_id,
            "category_name": category_name,
            "current_price": service.current_price,
            "is_active": service.is_active
        }
        return ServiceResponse(**service_dict)

    @staticmethod
    async def update_service_price(
        db: AsyncSession,
        service_id: int,
        data: UpdateServicePriceRequest
    ) -> ServiceResponse:
        """Update service price and record history"""
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio con ID {service_id} no encontrado"
            )

        # Check if price is different
        if service.current_price == data.new_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nuevo precio debe ser diferente al precio actual"
            )

        # Record price history
        price_history = PriceHistory(
            service_id=service.id,
            old_price=service.current_price,
            new_price=data.new_price
        )
        await PriceHistoryRepository.create(db, price_history)

        # Update service price
        service.current_price = data.new_price
        service = await ServiceRepository.update(db, service)

        category_name = "Sin categoría"
        if service.category:
            category_name = service.category.name
        else:
            logger.warning(f"El servicio con ID {service.id} tiene una categoría inválida (category_id: {service.category_id})")

        # Return response
        service_dict = {
            "id": service.id,
            "code": service.code,
            "name": service.name,
            "description": service.description,
            "category_id": service.category_id,
            "category_name": category_name,
            "current_price": service.current_price,
            "is_active": service.is_active
        }
        return ServiceResponse(**service_dict)

    @staticmethod
    async def get_price_history_by_service_id(db: AsyncSession, service_id: int) -> PriceHistoryListResponse:
        """Get all price history for a service"""
        # Check if service exists
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio con ID {service_id} no encontrado"
            )

        history = await PriceHistoryRepository.get_all_history(db, service_id)
        return PriceHistoryListResponse(
            price_history=[PriceHistoryResponse.model_validate(h) for h in history]
        )

    @staticmethod
    async def delete_service(db: AsyncSession, service_id: int) -> Dict[str, str]:
        """Delete service (soft delete)"""
        service = await ServiceRepository.get_by_id(db, service_id)
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Servicio con ID {service_id} no encontrado"
            )

        await ServiceRepository.delete(db, service)
        return {"message": f"Servicio '{service.name}' desactivado exitosamente"}

