"""
Patients Router - Proxy to patient-service
"""
from fastapi import APIRouter, Request, Response
from src.core.config import settings
from src.utils.proxy import proxy_request

router = APIRouter(prefix="/api/v1/patients", tags=["Patients"])


@router.get("")
async def list_patients(request: Request) -> Response:
    """List all patients (with pagination and filters)"""
    target_url = f"{settings.patient_service_url}/api/v1/patients"
    return await proxy_request(request, target_url)


@router.get("/{patient_id}")
async def get_patient(request: Request, patient_id: int) -> Response:
    """Get patient by ID"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}"
    return await proxy_request(request, target_url)


@router.post("")
async def create_patient(request: Request) -> Response:
    """Create new patient"""
    target_url = f"{settings.patient_service_url}/api/v1/patients"
    return await proxy_request(request, target_url)


@router.put("/{patient_id}")
async def update_patient(request: Request, patient_id: int) -> Response:
    """Update patient by ID"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}"
    return await proxy_request(request, target_url)


@router.delete("/{patient_id}")
async def delete_patient(request: Request, patient_id: int) -> Response:
    """Delete patient (soft delete)"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}"
    return await proxy_request(request, target_url)


@router.get("/{patient_id}/history")
async def get_patient_history(request: Request, patient_id: int) -> Response:
    """Get patient change history"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}/history"
    return await proxy_request(request, target_url)


@router.get("/{patient_id}/notes")
async def get_patient_notes(request: Request, patient_id: int) -> Response:
    """Get patient notes"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}/notes"
    return await proxy_request(request, target_url)


@router.post("/{patient_id}/notes")
async def add_patient_note(request: Request, patient_id: int) -> Response:
    """Add note to patient"""
    target_url = f"{settings.patient_service_url}/api/v1/patients/{patient_id}/notes"
    return await proxy_request(request, target_url)
