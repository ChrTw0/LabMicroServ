# src/utils/sunat_client.py

import base64
import zipfile
import io
from datetime import datetime

from src.core.config import settings


class SunatClient:
    """
    Cliente para conectar con SUNAT (versión mock funcional).
    Estructura preparada para reemplazar SOAP real en producción.
    """

    def __init__(self):
        """
        Inicializa con la configuración del sistema (SUNAT credentials, etc.).
        """
        self.ruc = settings.sunat_company_ruc
        self.user = settings.sunat_sol_user
        self.password = settings.sunat_sol_password
        self.endpoint = settings.sunat_pse_url
        self.cert_path = settings.sunat_cert_path
        self.cert_pass = settings.sunat_cert_pass

    # ============================================================
    # 1. BUILD XML (Generar XML UBL – aquí MOCK)
    # ============================================================
    def build_xml(self, invoice) -> str:
        """
        Construye el XML UBL. Por ahora: mock.
        """
        xml = f"""
        <Invoice>
            <ID>{invoice.id}</ID>
            <IssueDate>{invoice.created_at.date()}</IssueDate>
            <CustomerID>{invoice.patient_id}</CustomerID>
            <Total>{invoice.total:.2f}</Total>
        </Invoice>
        """
        return xml.strip()

    # Función mock para compatibilidad con imports antiguos
    def build_ubl_invoice_xml(self, invoice) -> str:
        return self.build_xml(invoice)

    # ============================================================
    # 2. SIGN XML (Firma digital)
    # ============================================================
    def sign_xml(self, xml_str: str) -> bytes:
        """
        Mock: codifica a bytes, simula firma digital.
        """
        return xml_str.encode("utf-8")

    # Función mock para compatibilidad con imports antiguos
    def sign_xml_placeholder(self, xml_str: str) -> bytes:
        return self.sign_xml(xml_str)

    # ============================================================
    # 3. CREATE ZIP FROM XML
    # ============================================================
    def create_zip_from_xml(self, xml_bytes: bytes, filename="invoice.xml") -> bytes:
        """
        Empaqueta el XML en un ZIP (mock).
        """
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(filename, xml_bytes)
        return buffer.getvalue()

    # ============================================================
    # 4. SEND TO SUNAT (Simulación)
    # ============================================================
    def send_to_sunat(self, xml_bytes: bytes) -> dict:
        """
        Mock: simula envío a SUNAT.
        """
        zip_content = self.create_zip_from_xml(xml_bytes)
        cdr_content = self._mock_cdr_success()
        return {
            "zip_sent": zip_content,
            "cdr_zip": cdr_content,
            "success": True,
            "message": "XML recibido exitosamente por SUNAT (mock)."
        }

    # ============================================================
    # 5. PROCESS CDR (Analizar respuesta)
    # ============================================================
    def process_cdr(self, cdr_zip: bytes) -> dict:
        """
        Descomprime CDR y evalúa status.
        """
        with zipfile.ZipFile(io.BytesIO(cdr_zip), "r") as z:
            cdr_xml = z.read("cdr.xml").decode("utf-8")

        status = "ACCEPTED" if "0" in cdr_xml else "REJECTED"
        return {
            "status": status,
            "cdr_xml": cdr_xml
        }

    # ============================================================
    # Utilidad interna (Mock CDR)
    # ============================================================
    def _mock_cdr_success(self) -> bytes:
        """
        Crea CDR ficticio (SUNAT normalmente genera R-XXXX.xml).
        """
        cdr_xml = f"""
        <CDR>
            <ResponseCode>0</ResponseCode>
            <Description>Comprobante aceptado por SUNAT</Description>
            <Timestamp>{datetime.now().isoformat()}</Timestamp>
        </CDR>
        """.strip()

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("cdr.xml", cdr_xml)

        return buffer.getvalue()

# src/utils/sunat_client.py

sunat_client = SunatClient()  # instancia global

def build_ubl_invoice_xml(invoice):
    return sunat_client.build_xml(invoice)

def sign_xml_placeholder(xml_str):
    return sunat_client.sign_xml(xml_str)

def create_zip_from_xml(xml_bytes):
    return sunat_client.send_to_sunat(xml_bytes)["zip_sent"]
