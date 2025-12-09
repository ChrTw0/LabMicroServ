"""
Billing Service (Business logic) - Versión corregida con fix de comunicación
Funcionalidades completas:
 - Generación de comprobante desde orden
 - Creación XML UBL corregido
 - Placeholder de firma digital
 - Creación de ZIP y envío a SUNAT
 - Parseo de CDR y actualización de estado
 - Envío opcional de correo con adjuntos
 - CRUD completo de facturas
"""

import io
import zipfile
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
    InvoiceItemResponse, InvoiceStats,
    SalesByPeriodStats, InvoiceTypeStats
)

from src.core.config import settings
from src.utils.sunat_client import SunatClient
from src.modules.sunat_integration.xml_generator import UBLXMLGenerator
from src.modules.sunat_integration.sunat_client import SUNATClient

logger = logging.getLogger(__name__)
sunat_client = SunatClient()

# Nuevos clientes SUNAT
xml_generator = UBLXMLGenerator()
# Por defecto usamos ambiente Beta (pruebas)
sunat_ws_client = SUNATClient.create_beta_client()


# ========================================
# HELPERS: XML / SIGNING / ZIP
# ========================================

def build_ubl_invoice_xml(invoice: Invoice) -> str:
    """
    Construye XML UBL 2.1 completo usando el nuevo generador.
    """
    # Mapeo de tipo de comprobante a código SUNAT
    tipo_comprobante_map = {
        InvoiceType.FACTURA: "01",
        InvoiceType.BOLETA: "03"
    }

    # Preparar datos del comprobante
    invoice_data = {
        "tipo_comprobante": tipo_comprobante_map.get(invoice.invoice_type, "01"),
        "serie": invoice.invoice_number.split("-")[0],
        "numero": int(invoice.invoice_number.split("-")[1]),
        "fecha_emision": invoice.issue_date,
        "moneda": "PEN",
        "subtotal": invoice.subtotal,
        "igv": invoice.tax,
        "total": invoice.total,
    }

    # Datos de la empresa emisora
    company_data = {
        "ruc": settings.sunat_company_ruc,
        "razon_social": getattr(settings, "company_name", "MI EMPRESA SAC"),
        "nombre_comercial": getattr(settings, "company_trade_name", "MI EMPRESA"),
        "direccion": getattr(settings, "company_address", "Av. Principal 123"),
        "ciudad": "LIMA",
        "departamento": "LIMA",
        "distrito": "LIMA",
    }

    # Datos del cliente
    tipo_doc_map = {
        "DNI": "1",
        "RUC": "6",
        "CE": "4",
        "PASAPORTE": "7"
    }

    client_data = {
        "tipo_documento": tipo_doc_map.get(invoice.customer_document_type, "6"),
        "numero_documento": invoice.customer_document_number,
        "razon_social": invoice.customer_name if invoice.invoice_type == InvoiceType.FACTURA else None,
        "nombres_completos": invoice.customer_name if invoice.invoice_type == InvoiceType.BOLETA else None,
    }

    # Items del comprobante
    items = []
    total_base_imponible = Decimal("0.00")
    total_igv = Decimal("0.00")

    for item in invoice.items:
        # Para SUNAT, siempre calcular valores base e IGV
        # Los precios en la BD ya incluyen IGV (precio de venta)
        precio_incluye_igv = item.unit_price
        valor_unitario = precio_incluye_igv / Decimal("1.18")  # Base imponible
        igv_unitario = precio_incluye_igv - valor_unitario  # IGV por unidad
        igv_total_item = igv_unitario * item.quantity
        base_total_item = valor_unitario * item.quantity

        # Acumular totales
        total_base_imponible += base_total_item
        total_igv += igv_total_item

        items.append({
            "codigo": item.service_code or f"SERV{item.id}",
            "descripcion": item.service_name,
            "cantidad": float(item.quantity),
            "unidad_medida": "NIU",  # Unidad
            "valor_unitario": float(valor_unitario),  # Base sin IGV
            "precio_unitario": float(precio_incluye_igv),  # Precio con IGV
            "subtotal": float(base_total_item),  # Base total
            "igv": float(igv_total_item),  # IGV del item
            "total": float(item.subtotal),  # Total con IGV
        })

    # Recalcular totales del comprobante basándose en los items calculados
    invoice_data["subtotal"] = total_base_imponible
    invoice_data["igv"] = total_igv
    # total permanece igual (es el total con IGV de la BD)

    # Generar XML usando el nuevo generador
    xml_content = xml_generator.generate_invoice(
        invoice_data=invoice_data,
        company_data=company_data,
        client_data=client_data,
        items=items
    )

    return xml_content


def sign_xml_placeholder(xml_str: str) -> bytes:
    """
    Firma XML usando certificado autofirmado para pruebas en SUNAT Beta.
    Para producción: usar certificado .pfx/.pem real de SUNAT.
    """
    from lxml import etree
    from signxml import XMLSigner
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    import datetime

    try:
        # Generar clave privada RSA temporal para pruebas
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )

        # Generar certificado autofirmado temporal
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "PE"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Lima"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Lima"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "EMPRESA DE PRUEBA"),
            x509.NameAttribute(NameOID.COMMON_NAME, "20000000001"),
        ])

        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).sign(private_key, hashes.SHA256())

        # Convertir certificado a PEM
        cert_pem = cert.public_bytes(serialization.Encoding.PEM)
        key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Parsear XML
        root = etree.fromstring(xml_str.encode('utf-8'))

        # Buscar UBLExtensions donde va la firma
        ns = {'ext': 'urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2'}
        ext_content = root.find('.//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent', ns)

        if ext_content is None:
            logger.error("No se encontró ExtensionContent para insertar la firma")
            return xml_str.encode("utf-8")

        # Firmar usando signxml
        # signxml agregará la firma al elemento raíz, pero necesitamos moverla a ExtensionContent
        from signxml import methods
        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha256",
            digest_algorithm="sha256",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )

        # Firmar el documento completo
        signed_root = signer.sign(
            root,
            key=key_pem,
            cert=cert_pem
        )

        # Buscar la firma que signxml agregó (usualmente al final del documento)
        ds_ns = {'ds': 'http://www.w3.org/2000/09/xmldsig#'}
        signature_elem = signed_root.find('.//ds:Signature', ds_ns)

        if signature_elem is not None:
            # Mover la firma al ExtensionContent
            ext_content_new = signed_root.find('.//ext:UBLExtensions/ext:UBLExtension/ext:ExtensionContent', ns)
            if ext_content_new is not None:
                # Remover la firma de su ubicación actual
                signature_elem.getparent().remove(signature_elem)
                # Agregar la firma dentro de ExtensionContent
                ext_content_new.append(signature_elem)
                logger.info("✅ XML firmado correctamente con certificado de prueba")
            else:
                logger.warning("No se pudo mover la firma a ExtensionContent")
        else:
            logger.warning("No se encontró la firma generada por signxml")

        return etree.tostring(signed_root, encoding='utf-8', xml_declaration=True)

    except Exception as e:
        logger.error(f"Error al firmar XML: {e}")
        logger.warning("⚠️  Enviando XML SIN FIRMA DIGITAL")
        return xml_str.encode("utf-8")


def create_zip_from_xml(xml_bytes: bytes, filename_without_ext: str) -> bytes:
    """Empaqueta el XML firmado en un ZIP para SUNAT."""
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{filename_without_ext}.xml", xml_bytes)
    return mem.getvalue()


# ========================================
# SMTP HELPER
# ========================================

async def send_email_with_attachments_async(
    to_email: str,
    subject: str,
    body: str,
    attachments: Optional[List[dict]] = None
):
    """
    Envía correo con adjuntos de forma asíncrona.
    attachments: list of dict with keys: filename, content (bytes), maintype, subtype
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
                msg.add_attachment(
                    att["content"],
                    maintype=att.get("maintype", "application"),
                    subtype=att.get("subtype", "octet-stream"),
                    filename=att["filename"]
                )

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

    return await asyncio.to_thread(_send_sync)


# ========================================
# SUNAT HELPERS
# ========================================

def parse_sendbill_result_to_status(send_result: dict) -> InvoiceStatus:
    """Normaliza la respuesta del SunatClient a InvoiceStatus."""
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
    Guarda información del CDR y actualiza estado del comprobante.
    Opcional: agregar columnas para persistir CDR ZIP/XML en modelo.
    """
    invoice.invoice_status = parse_sendbill_result_to_status(send_result)
    # Opcional: invoice.cdr_zip_path = "..."
    # Opcional: invoice.sunat_message = send_result.get("sunat_message")
    await InvoiceRepository.update(db, invoice)


# ========================================
# MAIN SERVICE CLASS
# ========================================

class InvoiceService:
    """Business logic completo para operaciones de facturación."""

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
        """Obtiene lista paginada de comprobantes con filtros."""
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
        """Obtiene detalle de un comprobante por ID."""
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante con ID {invoice_id} no encontrado"
            )
        return InvoiceService._to_detail_response(invoice)

    @staticmethod
    async def get_invoice_by_order(db: AsyncSession, order_id: int) -> InvoiceDetailResponse:
        """Obtiene comprobante asociado a una orden."""
        invoice = await InvoiceRepository.get_by_order_id(db, order_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró comprobante para la orden {order_id}"
            )
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice.id)
        return InvoiceService._to_detail_response(invoice)

    @staticmethod
    def _to_detail_response(invoice: Invoice) -> InvoiceDetailResponse:
        """Convierte entidad Invoice a InvoiceDetailResponse."""
        return InvoiceDetailResponse(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            order_id=invoice.order_id,
            patient_id=invoice.patient_id,
            location_id=invoice.location_id,
            invoice_type=invoice.invoice_type,
            invoice_status=invoice.invoice_status,
            customer_document_type=invoice.customer_document_type,
            customer_document_number=invoice.customer_document_number,
            customer_name=invoice.customer_name,
            customer_address=invoice.customer_address,
            subtotal=invoice.subtotal,
            tax=invoice.tax,
            total=invoice.total,
            issue_date=invoice.issue_date,
            created_at=invoice.created_at,
            items=[InvoiceItemResponse.model_validate(item) for item in invoice.items]
        )

    @staticmethod
    async def create_invoice_from_order(
        db: AsyncSession,
        data: InvoiceCreate,
        send_now: bool = False
    ) -> InvoiceDetailResponse:
        """
        Crea un comprobante desde una orden.
        - Comunicación corregida con order-service y patient-service usando settings
        """
        # 1) Validar que no exista comprobante para la orden
        existing = await InvoiceRepository.get_by_order_id(db, data.order_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un comprobante para la orden {data.order_id}"
            )
        existing_invoices = await InvoiceRepository.get_all_by_order_id(db, data.order_id)
        if existing_invoices:
            # Permitir crear uno nuevo solo si TODOS los anteriores están anulados
            if not all(inv.invoice_status == InvoiceStatus.CANCELLED for inv in existing_invoices):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Ya existe un comprobante activo o pendiente para la orden {data.order_id}. Anule el comprobante existente antes de crear uno nuevo."
                )

        # 2) Consultar order-service (corrección aplicada)
        try:
            async with httpx.AsyncClient(base_url=settings.order_service_url) as client:
                order_resp = await client.get(f"/api/v1/orders/{data.order_id}", timeout=10.0)
                if order_resp.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Orden {data.order_id} no encontrada"
                    )
                order_resp.raise_for_status()
                order_data = order_resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error al comunicarse con order-service: {str(e)}"
            )

        # 3) Consultar patient-service (corrección aplicada)
        patient_id = order_data["patient_id"]
        try:
            async with httpx.AsyncClient(base_url=settings.patient_service_url) as client:
                patient_resp = await client.get(f"/api/v1/patients/{patient_id}", timeout=10.0)
                if patient_resp.status_code == 404:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Paciente {patient_id} no encontrado"
                    )
                patient_resp.raise_for_status()
                patient_data = patient_resp.json()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Error al comunicarse con patient-service: {str(e)}"
            )

        # 4) Validación: FACTURA requiere RUC
        if data.invoice_type == InvoiceType.FACTURA and patient_data["document_type"] != "RUC":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Las facturas solo pueden emitirse para clientes con RUC"
            )

        # 5) Preparar datos del cliente
        customer_name = (
            patient_data["business_name"] 
            if patient_data["document_type"] == "RUC" 
            else f"{patient_data.get('first_name','')} {patient_data.get('last_name','')}".strip()
        )

        # 6) Calcular montos
        subtotal = Decimal(str(order_data.get("total", "0.00")))
        igv_rate = Decimal(str(getattr(settings, "igv_rate", "0.00")))
        tax = (subtotal * igv_rate).quantize(Decimal("0.01")) if igv_rate else Decimal("0.00")
        total = (subtotal + tax).quantize(Decimal("0.01"))

        # 7) Generar número correlativo
        invoice_number = await InvoiceRepository.generate_invoice_number(db, data.invoice_type)

        # 8) Crear entidad Invoice
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

        # 9) Crear items
        invoice_items = []
        for order_item in order_data.get("items", []):
            item = InvoiceItem(
                invoice_id=invoice.id,
                service_code=order_item.get("service_code"),  # Código del servicio
                service_name=order_item.get("service_name", ""),
                quantity=order_item.get("quantity", 1),
                unit_price=Decimal(str(order_item.get("unit_price", "0.00"))),
                subtotal=Decimal(str(order_item.get("subtotal", "0.00")))
            )
            invoice_items.append(item)

        await InvoiceItemRepository.create_many(db, invoice_items)

        # 10) Envío opcional a SUNAT
        if send_now:
            try:
                await InvoiceService.generate_and_send_to_sunat(db, invoice.id)
            except Exception as e:
                logger.exception(f"Error al enviar a SUNAT: {str(e)}")

        # 11) Retornar detalle
        return await InvoiceService.get_invoice_by_id(db, invoice.id)

    @staticmethod
    async def update_invoice_status(
        db: AsyncSession,
        invoice_id: int,
        data: InvoiceUpdateStatus
    ) -> InvoiceResponse:
        """Actualiza el estado de un comprobante."""
        invoice = await InvoiceRepository.get_by_id(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante con ID {invoice_id} no encontrado"
            )

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
        """Anula un comprobante."""
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
        """Obtiene estadísticas de facturación."""
        stats = await InvoiceRepository.get_statistics(db, date_from, date_to)
        return InvoiceStats(**stats)

    @staticmethod
    async def generate_and_send_to_sunat(
        db: AsyncSession,
        invoice_id: int
    ) -> InvoiceDetailResponse:
        """
        Flujo completo de envío a SUNAT:
         1. Cargar comprobante con ítems
         2. Generar XML UBL
         3. Firmar XML (placeholder)
         4. Crear ZIP
         5. Enviar a SUNAT via SunatClient
         6. Parsear CDR y actualizar estado
         7. Enviar correo con adjuntos (XML/ZIP/CDR)
        """
        # 1) Cargar invoice
        invoice = await InvoiceRepository.get_by_id_with_items(db, invoice_id)
        if not invoice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comprobante {invoice_id} no encontrado"
            )

        # 2) Generar XML UBL
        xml = build_ubl_invoice_xml(invoice)

        # 3) Firmar XML
        signed_xml_bytes = sign_xml_placeholder(xml)

        # Convertir bytes a string para el cliente SUNAT
        signed_xml_str = signed_xml_bytes.decode('utf-8')

        # 4) Crear ZIP (ya no es necesario para el nuevo cliente)
        # El nuevo cliente SUNATClient crea el ZIP internamente

        # 5) Enviar a SUNAT
        try:
            # Usar el nuevo cliente SUNAT con el XML firmado
            # Formato del filename: RUC-TIPO-SERIE-NUMERO
            # Ejemplo: 20000000001-03-B001-00000001
            tipo_doc = "01" if invoice.invoice_type == InvoiceType.FACTURA else "03"
            xml_filename = f"{settings.sunat_company_ruc}-{tipo_doc}-{invoice.invoice_number}"
            send_result = await sunat_ws_client.send_bill(
                xml_content=signed_xml_str,  # XML firmado como string
                filename=xml_filename
            )
        except Exception as e:
            logger.exception("Error enviando a SUNAT")
            invoice.invoice_status = InvoiceStatus.REJECTED
            await InvoiceRepository.update(db, invoice)
            raise

        # 6) Guardar CDR y actualizar estado
        await save_cdr_files_and_update_invoice(db, invoice, send_result)

        # 7) Envío de correo si SMTP configurado
        if getattr(settings, "smtp_host", None):
            # Obtener email del paciente
            try:
                async with httpx.AsyncClient() as client:
                    patient_resp = await client.get(
                        f"{settings.patient_service_url}/api/v1/patients/{invoice.patient_id}",
                        timeout=10.0
                    )
                    if patient_resp.status_code == 200:
                        patient_data = patient_resp.json()
                        patient_email = patient_data.get("email")
                    else:
                        patient_email = None
            except Exception:
                patient_email = None

            if patient_email:
                attachments = [
                    {
                        "filename": f"{filename_base}.xml",
                        "content": signed_xml_bytes,
                        "maintype": "application",
                        "subtype": "xml"
                    },
                    {
                        "filename": f"{filename_base}.zip",
                        "content": zip_bytes,
                        "maintype": "application",
                        "subtype": "zip"
                    }
                ]
                
                # Agregar CDR si existe
                if send_result.get("cdr_zip"):
                    attachments.append({
                        "filename": f"{filename_base}_cdr.zip",
                        "content": send_result.get("cdr_zip"),
                        "maintype": "application",
                        "subtype": "zip"
                    })

                # Enviar email
                subject = f"Comprobante {invoice.invoice_number}"
                body = f"Adjunto el comprobante electrónico {invoice.invoice_number} y su CDR."
                await send_email_with_attachments_async(patient_email, subject, body, attachments)

        return await InvoiceService.get_invoice_by_id(db, invoice.id)

    # ==================== REPORTING METHODS ====================

    @staticmethod
    async def get_sales_by_period_report(
        db: AsyncSession,
        months: int = 12,
        location_id: Optional[int] = None
    ) -> List[SalesByPeriodStats]:
        """Get sales report by period (monthly) - RF-075"""
        from sqlalchemy import func, select
        from datetime import datetime, timedelta

        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30 * months)

        # Build query - usar literal_column para evitar problemas con PostgreSQL
        from sqlalchemy import literal_column

        period_expr = func.to_char(Invoice.issue_date, 'YYYY-MM')

        query = select(
            period_expr.label('period'),
            func.sum(Invoice.total).label('total_sales'),
            func.count(Invoice.id).label('total_invoices'),
            func.sum(Invoice.tax).label('total_tax')
        ).where(
            Invoice.invoice_status != InvoiceStatus.CANCELLED,
            Invoice.issue_date >= start_date
        )

        if location_id:
            query = query.where(Invoice.location_id == location_id)

        query = query.group_by(literal_column('period'))
        query = query.order_by(literal_column('period'))

        result = await db.execute(query)
        rows = result.all()

        stats = []
        for row in rows:
            avg_value = row.total_sales / row.total_invoices if row.total_invoices > 0 else Decimal(0)
            stats.append(SalesByPeriodStats(
                period=row.period,
                total_sales=row.total_sales,
                total_invoices=row.total_invoices,
                total_tax=row.total_tax,
                avg_invoice_value=avg_value
            ))

        return stats

    @staticmethod
    async def get_invoice_type_report(
        db: AsyncSession,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        location_id: Optional[int] = None
    ) -> List[InvoiceTypeStats]:
        """Get statistics by invoice type (BOLETA/FACTURA) - RF-075"""
        from sqlalchemy import func, select

        # Build query
        query = select(
            Invoice.invoice_type,
            func.sum(Invoice.total).label('total_amount'),
            func.count(Invoice.id).label('count')
        ).where(Invoice.invoice_status != InvoiceStatus.CANCELLED)

        if date_from:
            query = query.where(Invoice.issue_date >= date_from)
        if date_to:
            query = query.where(Invoice.issue_date <= date_to)
        if location_id:
            query = query.where(Invoice.location_id == location_id)

        query = query.group_by(Invoice.invoice_type)

        result = await db.execute(query)
        rows = result.all()

        # Calculate total and percentages
        grand_total = sum(row.total_amount for row in rows) if rows else Decimal(0)

        stats = []
        for row in rows:
            percentage = float((row.total_amount / grand_total * 100)) if grand_total > 0 else 0.0
            avg_value = row.total_amount / row.count if row.count > 0 else Decimal(0)
            stats.append(InvoiceTypeStats(
                invoice_type=row.invoice_type.value,
                total_amount=row.total_amount,
                count=row.count,
                percentage=round(percentage, 2),
                avg_value=avg_value
            ))

        return stats