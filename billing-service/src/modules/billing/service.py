# billing-service/src/modules/billing/service.py
"""
Billing Service (Business logic) - Full version with SUNAT + SMTP skeleton
Reemplaza el service.py actual. Diseñado para:
 - generar factura desde orden
 - crear XML UBL (borrador/simple)
 - firmar XML (placeholder / interfaz)
 - crear ZIP y enviar a SUNAT mediante SunatClient
 - parsear CDR y guardar resultado
 - enviar correo con adjuntos (XML/ZIP/CDR) si SMTP está configurado
 - mantener compatibilidad con InvoiceRepository / InvoiceItemRepository
"""

import io
import zipfile
import base64
import logging
import asyncio
from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List

import httpx
from email.message import EmailMessage
import smtplib

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from src.modules.billing.models import Invoice, InvoiceItem, InvoiceType, InvoiceStatus
from src.modules.billing.repository import InvoiceRepository, InvoiceItemRepository
from src.modules.billing.schemas import (
    InvoiceCreate, InvoiceUpdateStatus,
    InvoiceResponse, InvoiceDetailResponse, InvoiceListResponse,
    InvoiceItemResponse, InvoiceStats
)

from src.core.config import settings
from src.utils.sunat_client import SunatClient

logger = logging.getLogger(__name__)

# Sunat client instance (wraps SOAP logic)
sunat_client = SunatClient()


# ------------------------------
# Helpers: XML / Signing / ZIP
# ------------------------------
def build_ubl_invoice_xml(invoice: Invoice) -> str:
    """
    Construye (plantilla simplificada) del XML UBL requerido por SUNAT.
    -> Debe ser reemplazado por una implementación UBL completa (UBL 2.1).
    """
    # Dates
    issue_date = invoice.issue_date.strftime("%Y-%m-%d") if isinstance(invoice.issue_date, datetime) else str(invoice.issue_date)

    # Basic XML (skeleton). Production: usar templates y UBL spec
    lines = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"',
        '         xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"',
        '         xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">',
        f'  <cbc:ID>{invoice.invoice_number}</cbc:ID>',
        f'  <cbc:IssueDate>{issue_date}</cbc:IssueDate>',
        '  <cac:LegalMonetaryTotal>',
        f'    <cbc:PayableAmount currencyID="PEN">{invoice.total:.2f}</cbc:PayableAmount>',
        '  </cac:LegalMonetaryTotal>',
        '  <cac:AccountingSupplierParty>',
        f'    <cbc:CustomerAssignedAccountID>{settings.sunat_company_ruc}</cbc:CustomerAssignedAccountID>',
        '    <cbc:AdditionalAccountID>6</cbc:AdditionalAccountID>',
        '  </cac:AccountingSupplierParty>',
        '  <cac:AccountingCustomerParty>',
        f'    <cbc:CustomerAssignedAccountID>{invoice.customer_document_number}</cbc:CustomerAssignedAccountID>',
        f'    <cbc:AdditionalAccountID>{"1" if invoice.customer_document_type=="DNI" else "6"}</cbc:AdditionalAccountID>',
        '  </cac:AccountingCustomerParty>',
        '  <cac:InvoiceLine>'
    ]
    for i, item in enumerate(invoice.items, start=1):
        lines += [
            f'    <cac:InvoiceLine>',
            f'      <cbc:ID>{i}</cbc:ID>',
            f'      <cbc:InvoicedQuantity>{item.quantity}</cbc:InvoicedQuantity>',
            f'      <cbc:LineExtensionAmount currencyID="PEN">{item.subtotal:.2f}</cbc:LineExtensionAmount>',
            f'      <cac:Item>',
            f'        <cbc:Description>{item.service_name}</cbc:Description>',
            f'      </cac:Item>',
            f'      <cac:Price>',
            f'        <cbc:PriceAmount currencyID="PEN">{item.unit_price:.2f}</cbc:PriceAmount>',
            f'      </cac:Price>',
            f'    </cac:InvoiceLine>'
        ]
    lines += [
        '  </cac:InvoiceLine>',
        '</Invoice>'
    ]
    xml = "\n".join(lines)
    return xml


def sign_xml_placeholder(xml_str: str) -> bytes:
    """
    Placeholder para firma digital.
    - En producción: implementar XAdES con PyXMLSecurity o usar herramientas externas.
    - Esta función devuelve bytes del 'xml firmado' (aquí base64 del xml para simular).
    """
    # TODO: implementar firma XAdES-BES con certificado .pfx/.pem
    # Ejemplo: xml_signed_bytes = sign_with_cert(xml_str, cert_path=settings.sunat_cert_path, cert_password=settings.sunat_cert_pass)
    xml_bytes = xml_str.encode("utf-8")
    # Como placeholder devolvemos el xml en bytes (no firmado)
    return xml_bytes


def create_zip_from_xml(xml_bytes: bytes, filename_without_ext: str) -> bytes:
    """
    Empaqueta el XML (firmado) en un ZIP con el nombre que SUNAT espera.
    Devuelve bytes del ZIP.
    """
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        xml_name = f"{filename_without_ext}.xml"
        zf.writestr(xml_name, xml_bytes)
    return mem.getvalue()


# ------------------------------
# SMTP helper (async wrapper)
# ------------------------------
async def send_email_with_attachments_async(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None
):
    """
    Envía correo con adjuntos usando smtplib en un hilo para no bloquear event loop.
    attachments: list of dict with keys: filename, content (bytes), mime (optional)
    """
    if not getattr(settings, "smtp_host", None):
        logger.warning("SMTP no configurado. Omitiendo envío de correo.")
        return {"status": "skipped", "reason": "smtp not configured"}

    def _send_sync():
        msg = EmailMessage()
        msg["From"] = getattr(settings, "smtp_from", "no-reply@labclinico.local")
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)

        if attachments:
            for att in attachments:
                filename = att["filename"]
                content = att["content"]
                maintype = att.get("maintype", "application")
                subtype = att.get("subtype", "octet-stream")
                msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=filename)

        # Conexión SMTP básica (no SSL) - admite TLS opcional
        host = settings.smtp_host
        port = int(getattr(settings, "smtp_port", 25))
        user = getattr(settings, "smtp_user", None)
        password = getattr(settings, "smtp_password", None)
        use_tls = bool(getattr(settings, "smtp_tls", False))

        s = smtplib.SMTP(host, port, timeout=30)
        try:
            if use_tls:
                s.starttls()
            if user and password:
                s.login(user, password)
            s.send_message(msg)
        finally:
            s.quit()
        return {"status": "sent"}

    # Ejecutar en hilo
    return await asyncio.to_thread(_send_sync)


# ------------------------------
# SUNAT / CDR processing helpers
# ------------------------------
def parse_sendbill_result_to_status(send_result: dict) -> InvoiceStatus:
    """
    Normaliza la respuesta del SunatClient a InvoiceStatus del modelo.
    """
    st = send_result.get("status", "").upper()
    if st in ("ACCEPTED", "ACEPTADO", "OK"):
        return InvoiceStatus.ACCEPTED
    if st in ("REJECTED", "RECHAZADO"):
        return InvoiceStatus.REJECTED
    if st in ("SENT",):
        return InvoiceStatus.SENT
    return InvoiceStatus.PENDING


async def save_cdr_files_and_update_invoice(
    db: AsyncSession,
    invoice: Invoice,
    send_result: dict
) -> None:
    """
    Guarda información del CDR en la DB (si es necesario) y actualiza estado.
    - Si quieres persistir archivos, agrega columnas en modelo y migra.
    """
    # Actualizar estado según respuesta
    new_status = parse_sendbill_result_to_status(send_result)
    invoice.invoice_status = new_status

    # Opcional: almacenar CDR ZIP y XML en FS o base (no implementado)
    # Ejemplo de campos a agregar mediante migration:
    # invoice.cdr_zip_path = "/data/cdrs/..."
    # invoice.cdr_xml = send_result.get("cdr_xml")
    # invoice.sunat_message = send_result.get("sunat_message")

    invoice = await InvoiceRepository.update(db, invoice)
    # commit handled by repository if needed (update commits)
    return


# ------------------------------
# MAIN SERVICE CLASS
# ------------------------------
class InvoiceService:
    """Business logic for Invoice operations (completo con SUNAT/SMTP)"""

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
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comprobante con ID {invoice_id} no encontrado")

        return InvoiceService._to_detail_response(invoice)

    @staticmethod
    async def get_invoice_by_order(db: AsyncSession, order_id: int) -> InvoiceDetailResponse:
        invoice = await InvoiceRepository.get_by_order_id(db, order_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No se encontró comprobante para la orden {order_id}")

        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice.id)
        return InvoiceService._to_detail_response(invoice)

    @staticmethod
    def _to_detail_response(invoice: Invoice) -> InvoiceDetailResponse:
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
        data: InvoiceCreate,
        send_now: bool = False  # si True: genera y envía a SUNAT en el mismo flujo
    ) -> InvoiceDetailResponse:
        """
        Crea un comprobante a partir de la orden (consulta order-service y patient-service),
        guarda en DB y opcionalmente lo envía a SUNAT (send_now).
        """
        # 1) Validar que no exista comprobante para la orden
        existing = await InvoiceRepository.get_by_order_id(db, data.order_id)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Ya existe un comprobante para la orden {data.order_id}")

        # 2) Consultar order-service
        try:
            async with httpx.AsyncClient() as client:
                order_resp = await client.get(f"{settings.order_service_url}/api/v1/orders/{data.order_id}", timeout=10.0)
                if order_resp.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Orden {data.order_id} no encontrada")
                order_resp.raise_for_status()
                order_data = order_resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Error al comunicarse con order-service: {str(e)}")

        # 3) Consultar patient-service
        patient_id = order_data["patient_id"]
        try:
            async with httpx.AsyncClient() as client:
                patient_resp = await client.get(f"{settings.patient_service_url}/api/v1/patients/{patient_id}", timeout=10.0)
                if patient_resp.status_code == 404:
                    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Paciente {patient_id} no encontrado")
                patient_resp.raise_for_status()
                patient_data = patient_resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Error al comunicarse con patient-service: {str(e)}")

        # 4) Validación de tipo (FACTURA requiere RUC)
        if data.invoice_type == InvoiceType.FACTURA and patient_data["document_type"] != "RUC":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Las facturas solo pueden emitirse para clientes con RUC")

        customer_name = patient_data["business_name"] if patient_data["document_type"] == "RUC" else f"{patient_data.get('first_name','')} {patient_data.get('last_name','')}".strip()

        # 5) Cálculos de montos (por ahora tax = 0, opción a usar settings.igv_rate cuando esté)
        subtotal = Decimal(str(order_data.get("total", "0.00")))
        # Si se quiere IGV configurable:
        igv_rate = Decimal(str(getattr(settings, "igv_rate", "0.00")))
        tax = (subtotal * igv_rate).quantize(Decimal("0.01")) if igv_rate and igv_rate != Decimal("0.00") else Decimal("0.00")
        total = (subtotal + tax).quantize(Decimal("0.01"))

        # 6) Generar número correlativo
        invoice_number = await InvoiceRepository.generate_invoice_number(db, data.invoice_type)

        # 7) Crear entidad y persistir
        invoice = Invoice(
            invoice_number=invoice_number,
            order_id=data.order_id,
            patient_id=patient_id,
            location_id=order_data.get("location_id", 0),
            invoice_type=data.invoice_type,
            invoice_status=InvoiceStatus.PENDING,
            customer_document_type=patient_data.get("document_type", ""),
            customer_document_number=patient_data.get("document_number", ""),
            customer_name=customer_name,
            customer_address=patient_data.get("address"),
            subtotal=subtotal,
            tax=tax,
            total=total
        )
        invoice = await InvoiceRepository.create(db, invoice)

        # 8) Crear items
        invoice_items = []
        for order_item in order_data.get("items", []):
            item = InvoiceItem(
                invoice_id=invoice.id,
                service_name=order_item.get("service_name", ""),
                quantity=order_item.get("quantity", 1),
                unit_price=Decimal(str(order_item.get("unit_price", "0.00"))),
                subtotal=Decimal(str(order_item.get("subtotal", "0.00")))
            )
            invoice_items.append(item)

        await InvoiceItemRepository.create_many(db, invoice_items)
        # Commit done in create_many or repository create/update

        # 9) Si send_now -> generar XML, firmar, zip, enviar y persistir CDR
        if send_now:
            try:
                await InvoiceService.generate_and_send_to_sunat(db, invoice.id)
            except Exception as e:
                logger.exception(f"Error al enviar a SUNAT: {str(e)}")
                # No fallamos la creación; el usuario puede reintentar enviar
        # 10) Return detalle
        return await InvoiceService.get_invoice_by_id(db, invoice.id)

    @staticmethod
    async def update_invoice_status(
        db: AsyncSession,
        invoice_id: int,
        data: InvoiceUpdateStatus
    ) -> InvoiceResponse:
        invoice = await InvoiceRepository.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comprobante con ID {invoice_id} no encontrado")

        if invoice.invoice_status == InvoiceStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede cambiar el estado de un comprobante anulado")

        invoice.invoice_status = data.invoice_status
        invoice = await InvoiceRepository.update(db, invoice)
        return InvoiceResponse.model_validate(invoice)

    @staticmethod
    async def cancel_invoice(db: AsyncSession, invoice_id: int) -> InvoiceResponse:
        invoice = await InvoiceRepository.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comprobante con ID {invoice_id} no encontrado")

        if invoice.invoice_status == InvoiceStatus.CANCELLED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El comprobante ya está anulado")

        invoice.invoice_status = InvoiceStatus.CANCELLED
        invoice = await InvoiceRepository.update(db, invoice)
        return InvoiceResponse.model_validate(invoice)

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None
    ) -> InvoiceStats:
        stats = await InvoiceRepository.get_statistics(db, date_from, date_to)
        return InvoiceStats(**stats)

    # -------------------------------
    # SUNAT / SEND FLOW
    # -------------------------------
    @staticmethod
    async def generate_and_send_to_sunat(db: AsyncSession, invoice_id: int) -> InvoiceDetailResponse:
        """
        Flujo completo:
         - cargar invoice (with items)
         - build UBL XML
         - sign XML (placeholder -> integrate real signer)
         - create ZIP
         - call SunatClient.send_bill
         - parse & save results (update invoice status)
         - optionally send email to customer with attachments (XML/ZIP/CDR)
        """
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
        if not invoice:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comprobante {invoice_id} no encontrado")

        # 1) Build XML
        xml = build_ubl_invoice_xml(invoice)

        # 2) Sign XML (placeholder -> bytes)
        signed_xml_bytes = sign_xml_placeholder(xml)

        # 3) Create ZIP
        filename_base = invoice.invoice_number.replace("-", "_")
        zip_bytes = create_zip_from_xml(signed_xml_bytes, filename_base)

        # 4) Send to SUNAT via SunatClient
        try:
            send_result = sunat_client.send_bill(signed_xml=signed_xml_bytes, invoice_filename=filename_base)
        except Exception as e:
            logger.exception("Error enviando a SUNAT")
            # Actualizamos estado a REJECTED o dejamos en PENDING según política
            invoice.invoice_status = InvoiceStatus.REJECTED
            await InvoiceRepository.update(db, invoice)
            raise

        # 5) Save CDR + update invoice status
        await save_cdr_files_and_update_invoice(db, invoice, send_result)

        # 6) If accepted and SMTP configured -> send email
        if getattr(settings, "smtp_host", None) and invoice.customer_document_number:
            # Resolve email from patient-service (optional)
            try:
                async with httpx.AsyncClient() as client:
                    patient_resp = await client.get(f"{settings.patient_service_url}/api/v1/patients/{invoice.patient_id}", timeout=10.0)
                    if patient_resp.status_code == 200:
                        patient_data = patient_resp.json()
                        patient_email = patient_data.get("email")
                    else:
                        patient_email = None
            except Exception:
                patient_email = None

            if patient_email:
                attachments = []
                # XML (signed) as .xml
                attachments.append({"filename": f"{filename_base}.xml", "content": signed_xml_bytes, "maintype": "application", "subtype": "xml"})
                # ZIP
                attachments.append({"filename": f"{filename_base}.zip", "content": zip_bytes, "maintype": "application", "subtype": "zip"})
                # CDR (if present)
                if send_result.get("cdr_zip"):
                    attachments.append({"filename": f"{filename_base}_cdr.zip", "content": send_result.get("cdr_zip"), "maintype": "application", "subtype": "zip"})
                # Send email (async)
                subject = f"Comprobante {invoice.invoice_number}"
                body = "Adjunto el comprobante electrónico y su CDR."
                await send_email_with_attachments_async(patient_email, subject, body, attachments)

        return await InvoiceService.get_invoice_by_id(db, invoice.id)
