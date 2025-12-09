"""
Internal Router for service-to-service communication
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.core.security import verify_internal_api_key
from src.services.user import UserService
from src.schemas.user import UserCreate
from src.schemas.auth import UserInfo

router = APIRouter(
    prefix="/api/v1/internal",
    tags=["Internal"],
    dependencies=[Depends(verify_internal_api_key)]
)

@router.post(
    "/create-patient-user",
    response_model=UserInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Create a user for a new patient"
)
async def create_patient_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a user for a new patient.
    This endpoint is for internal use by the patient-service.
    """
    # The created_by can be set to a system user or a default value
    return await UserService.create_user(db, data, created_by=1)
