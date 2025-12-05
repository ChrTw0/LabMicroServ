from fastapi import APIRouter, Depends, status, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from src.core.database import get_db
# Assuming security is handled by an API Gateway or a shared library
# from src.core.security import require_roles 
from . import service
from . import schemas

router = APIRouter(
    prefix="/api/v1/catalog",
    tags=["Catalog"],
    # dependencies=[Depends(require_roles("Administrador General", "Supervisor de Sede", "Recepcionista"))]
)

# Role-specific dependencies (example)
admin_supervisor_roles = [] # Depends(require_roles("Administrador General", "Supervisor de Sede"))

# --- Test Endpoints ---

@router.get("/tests", response_model=schemas.TestListResponse, summary="Listar o buscar pruebas de laboratorio")
async def get_all_tests(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    category_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(True),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene una lista paginada de pruebas de laboratorio.
    - Permite búsqueda por nombre o código.
    - Permite filtrar por categoría y estado.
    """
    return await service.get_all_tests(db, page, page_size, search, category_id, is_active)

@router.post("/tests", response_model=schemas.TestResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva prueba", dependencies=admin_supervisor_roles)
async def create_test(data: schemas.TestCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva prueba de laboratorio en el catálogo.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    return await service.create_test(db, data)

@router.get("/tests/{test_id}", response_model=schemas.TestResponse, summary="Obtener prueba por ID")
async def get_test_by_id(test_id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtiene los detalles de una prueba de laboratorio específica.
    """
    test = await service.get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return test

@router.put("/tests/{test_id}", response_model=schemas.TestResponse, summary="Actualizar prueba", dependencies=admin_supervisor_roles)
async def update_test(test_id: int, data: schemas.TestUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza los detalles de una prueba de laboratorio.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    updated_test = await service.update_test(db, test_id, data)
    if not updated_test:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return updated_test

@router.delete("/tests/{test_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Desactivar prueba", dependencies=admin_supervisor_roles)
async def delete_test(test_id: int, db: AsyncSession = Depends(get_db)):
    """
    Desactiva una prueba de laboratorio (soft delete).
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    success = await service.delete_test(db, test_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Test not found")
    return

# --- Category Endpoints ---

@router.get("/categories", response_model=List[schemas.CategoryResponse], summary="Listar todas las categorías")
async def get_all_categories(active_only: bool = True, db: AsyncSession = Depends(get_db)):
    """
    Obtiene una lista de todas las categorías de pruebas.
    """
    return await service.get_all_categories(db, active_only)

@router.post("/categories", response_model=schemas.CategoryResponse, status_code=status.HTTP_201_CREATED, summary="Crear nueva categoría", dependencies=admin_supervisor_roles)
async def create_category(data: schemas.CategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea una nueva categoría de pruebas.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    return await service.create_category(db, data)

@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse, summary="Actualizar categoría", dependencies=admin_supervisor_roles)
async def update_category(category_id: int, data: schemas.CategoryUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza una categoría de pruebas.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    updated_category = await service.update_category(db, category_id, data)
    if not updated_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return updated_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar categoría", dependencies=admin_supervisor_roles)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina una categoría si no tiene pruebas asociadas.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    try:
        await service.delete_category(db, category_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return

# --- SampleType Endpoints ---

@router.get("/sample-types", response_model=List[schemas.SampleTypeResponse], summary="Listar todos los tipos de muestra")
async def get_all_sample_types(active_only: bool = True, db: AsyncSession = Depends(get_db)):
    """
    Obtiene una lista de todos los tipos de muestra.
    """
    return await service.get_all_sample_types(db, active_only)

@router.post("/sample-types", response_model=schemas.SampleTypeResponse, status_code=status.HTTP_201_CREATED, summary="Crear nuevo tipo de muestra", dependencies=admin_supervisor_roles)
async def create_sample_type(data: schemas.SampleTypeCreate, db: AsyncSession = Depends(get_db)):
    """
    Crea un nuevo tipo de muestra.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    return await service.create_sample_type(db, data)

@router.put("/sample-types/{sample_type_id}", response_model=schemas.SampleTypeResponse, summary="Actualizar tipo de muestra", dependencies=admin_supervisor_roles)
async def update_sample_type(sample_type_id: int, data: schemas.SampleTypeUpdate, db: AsyncSession = Depends(get_db)):
    """
    Actualiza un tipo de muestra.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    updated_sample_type = await service.update_sample_type(db, sample_type_id, data)
    if not updated_sample_type:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample type not found")
    return updated_sample_type

@router.delete("/sample-types/{sample_type_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar tipo de muestra", dependencies=admin_supervisor_roles)
async def delete_sample_type(sample_type_id: int, db: AsyncSession = Depends(get_db)):
    """
    Elimina un tipo de muestra si no tiene pruebas asociadas.
    - **Requiere rol:** Administrador General o Supervisor de Sede
    """
    try:
        await service.delete_sample_type(db, sample_type_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception:
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sample type not found")
    return