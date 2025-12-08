"""
SUNAT Client - Envío de comprobantes electrónicos a SUNAT
Soporta ambiente Beta (pruebas) y Producción
"""
import base64
import httpx
from typing import Dict, Optional, Tuple
from loguru import logger
from lxml import etree
import zipfile
import io


class SUNATClient:
    """Cliente para envío de comprobantes a SUNAT via SOAP"""

    # URLs de webservices SUNAT
    BETA_URL = "https://e-beta.sunat.gob.pe/ol-ti-itcpfegem-beta/billService"
    PROD_URL = "https://e-factura.sunat.gob.pe/ol-ti-itcpfegem/billService"

    # Credenciales de prueba SUNAT (ambiente Beta)
    BETA_CREDENTIALS = {
        "ruc": "20000000001",
        "usuario": "MODDATOS",
        "password": "MODDATOS"
    }

    def __init__(self, ruc: str, usuario: str, password: str, produccion: bool = False):
        """
        Inicializar cliente SUNAT

        Args:
            ruc: RUC del emisor
            usuario: Usuario SOL
            password: Clave SOL
            produccion: True para producción, False para Beta
        """
        self.ruc = ruc
        self.usuario = usuario
        self.password = password
        self.produccion = produccion
        self.url = self.PROD_URL if produccion else self.BETA_URL

        logger.info(f"SUNAT Client inicializado - {'PRODUCCIÓN' if produccion else 'BETA'}")

    async def send_bill(self, xml_content: str, filename: str) -> Dict:
        """
        Enviar comprobante a SUNAT (sendBill)

        Args:
            xml_content: XML del comprobante (string)
            filename: Nombre del archivo (ej: 20000000001-01-F001-00000001)

        Returns:
            Dict con respuesta SUNAT (éxito/error, CDR)
        """
        try:
            logger.info(f"Enviando comprobante a SUNAT: {filename}")

            # 1. Crear ZIP con el XML
            zip_content = self._create_zip(xml_content, f"{filename}.xml")

            # 2. Codificar ZIP en base64
            zip_b64 = base64.b64encode(zip_content).decode("utf-8")

            # 3. Crear sobre SOAP
            soap_request = self._create_soap_envelope(
                f"{filename}.zip",
                zip_b64
            )

            # Debug: Loggear primeros caracteres del SOAP request
            logger.debug(f"SOAP Request (primeros 500 chars): {soap_request[:500]}")
            logger.debug(f"ZIP filename: {filename}.zip")
            logger.debug(f"ZIP size: {len(zip_content)} bytes")

            # 4. Enviar a SUNAT
            response = await self._send_soap_request(soap_request)

            # 5. Procesar respuesta
            result = self._parse_response(response)

            # Loggear respuesta detallada
            if result.get('success'):
                logger.info(f"✅ SUNAT ACEPTÓ el comprobante: {filename}")
                logger.info(f"   Estado: {result.get('status')}")
            else:
                logger.error(f"❌ SUNAT RECHAZÓ el comprobante: {filename}")
                logger.error(f"   Estado: {result.get('status')}")
                logger.error(f"   Error: {result.get('error', 'No especificado')}")
                logger.error(f"   Fault Code: {result.get('fault_code', 'N/A')}")
                logger.error(f"   Fault String: {result.get('fault_string', 'N/A')}")
                logger.error(f"   Response completo: {result}")

            return result

        except Exception as e:
            logger.error(f"Error enviando comprobante a SUNAT: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": "ERROR"
            }

    def _create_zip(self, xml_content: str, xml_filename: str) -> bytes:
        """Crear archivo ZIP con el XML"""
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr(xml_filename, xml_content.encode('utf-8'))

        return zip_buffer.getvalue()

    def _create_soap_envelope(self, filename: str, content_b64: str) -> str:
        """Crear sobre SOAP para sendBill"""
        # Username debe ser RUC + USUARIO (ej: 20000000001MODDATOS)
        username = f"{self.ruc}{self.usuario}"

        soap_envelope = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ser="http://service.sunat.gob.pe" xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd">
<soapenv:Header>
<wsse:Security>
<wsse:UsernameToken>
<wsse:Username>{username}</wsse:Username>
<wsse:Password>{self.password}</wsse:Password>
</wsse:UsernameToken>
</wsse:Security>
</soapenv:Header>
<soapenv:Body>
<ser:sendBill>
<fileName>{filename}</fileName>
<contentFile>{content_b64}</contentFile>
</ser:sendBill>
</soapenv:Body>
</soapenv:Envelope>'''

        return soap_envelope

    async def _send_soap_request(self, soap_request: str) -> str:
        """Enviar request SOAP a SUNAT"""
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": ""
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.url,
                    content=soap_request.encode('utf-8'),
                    headers=headers,
                    timeout=30.0
                )

                # Si hay error, capturar el body para debug
                if response.status_code != 200:
                    logger.error(f"SUNAT respondió con status {response.status_code}")
                    logger.error(f"Response body: {response.text[:1000]}")

                response.raise_for_status()
                return response.text

        except httpx.HTTPError as e:
            logger.error(f"Error HTTP enviando a SUNAT: {e}")
            raise

    def _parse_response(self, response_xml: str) -> Dict:
        """Parsear respuesta SOAP de SUNAT"""
        try:
            # Parsear XML de respuesta
            root = etree.fromstring(response_xml.encode('utf-8'))

            # Buscar fault (error)
            fault = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
            if fault is not None:
                fault_code = fault.findtext("./faultcode")
                fault_string = fault.findtext("./faultstring")

                return {
                    "success": False,
                    "status": "RECHAZADO",
                    "error": f"{fault_code}: {fault_string}",
                    "fault_code": fault_code,
                    "fault_string": fault_string
                }

            # Buscar sendBillResponse (éxito)
            response_elem = root.find(".//{http://service.sunat.gob.pe}sendBillResponse")
            if response_elem is None:
                return {
                    "success": False,
                    "status": "ERROR",
                    "error": "No se encontró respuesta válida de SUNAT"
                }

            # Obtener applicationResponse (CDR en base64)
            app_response = response_elem.findtext("./applicationResponse")
            if not app_response:
                logger.warning("⚠️  SUNAT no devolvió CDR, pero tampoco hubo error")
                # SUNAT aceptó el comprobante aunque no haya CDR
                return {
                    "success": True,
                    "status": "ACEPTADO",
                    "error": "CDR no disponible",
                    "response_code": "0",
                    "response_description": "Aceptado por SUNAT (sin CDR)"
                }

            # Decodificar CDR (ZIP)
            cdr_zip = base64.b64decode(app_response)
            logger.debug(f"CDR ZIP size: {len(cdr_zip)} bytes")

            # Extraer XML del CDR
            cdr_xml = self._extract_cdr_from_zip(cdr_zip)
            logger.debug(f"CDR XML size: {len(cdr_xml)} bytes")

            # Si el CDR está vacío (común en Beta), asumir que fue aceptado
            if not cdr_xml or len(cdr_xml.strip()) == 0:
                logger.warning("⚠️  CDR vacío recibido de SUNAT Beta")
                return {
                    "success": True,
                    "status": "ACEPTADO",
                    "response_code": "0",
                    "response_description": "Aceptado por SUNAT Beta (CDR vacío)",
                    "cdr_zip_b64": app_response,
                    "notes": ["CDR vacío - común en ambiente Beta de SUNAT"]
                }

            # Parsear CDR para obtener estado
            cdr_data = self._parse_cdr(cdr_xml)

            return {
                "success": True,
                "status": cdr_data.get("status", "ACEPTADO"),
                "cdr_xml": cdr_xml,
                "cdr_zip_b64": app_response,
                "response_code": cdr_data.get("response_code"),
                "response_description": cdr_data.get("response_description"),
                "notes": cdr_data.get("notes", [])
            }

        except Exception as e:
            logger.error(f"Error parseando respuesta SUNAT: {e}")
            return {
                "success": False,
                "status": "ERROR",
                "error": f"Error parseando respuesta: {str(e)}"
            }

    def _extract_cdr_from_zip(self, zip_content: bytes) -> str:
        """Extraer XML del CDR desde el ZIP"""
        with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_file:
            # El CDR siempre tiene un solo archivo XML
            xml_filename = zip_file.namelist()[0]
            cdr_xml = zip_file.read(xml_filename).decode('utf-8')
            return cdr_xml

    def _parse_cdr(self, cdr_xml: str) -> Dict:
        """Parsear CDR (Constancia de Recepción)"""
        try:
            root = etree.fromstring(cdr_xml.encode('utf-8'))

            # ResponseCode (0=Aceptado, 0XXX=Aceptado con observaciones, otros=Rechazado)
            response_code = root.findtext(
                ".//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ResponseCode"
            )

            # Description
            description = root.findtext(
                ".//{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Description"
            )

            # Notes (observaciones)
            notes = []
            for note_elem in root.findall(
                ".//{urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1}Note"
            ):
                notes.append(note_elem.text)

            # Determinar estado
            if response_code == "0":
                status = "ACEPTADO"
            elif response_code and response_code.startswith("0"):
                status = "ACEPTADO_CON_OBSERVACIONES"
            else:
                status = "RECHAZADO"

            return {
                "status": status,
                "response_code": response_code,
                "response_description": description,
                "notes": notes
            }

        except Exception as e:
            logger.error(f"Error parseando CDR: {e}")
            return {
                "status": "ERROR",
                "error": str(e)
            }

    @classmethod
    def create_beta_client(cls) -> 'SUNATClient':
        """Crear cliente para ambiente Beta (pruebas)"""
        creds = cls.BETA_CREDENTIALS
        return cls(
            ruc=creds["ruc"],
            usuario=creds["usuario"],
            password=creds["password"],
            produccion=False
        )

    def get_status(self, ruc_emisor: str, tipo_doc: str, serie: str, numero: int) -> Dict:
        """
        Consultar estado de comprobante (getStatus)

        Args:
            ruc_emisor: RUC del emisor
            tipo_doc: Tipo de documento (01, 03, etc.)
            serie: Serie del comprobante
            numero: Número del comprobante

        Returns:
            Dict con estado del comprobante
        """
        # TODO: Implementar getStatus
        logger.warning("getStatus no implementado aún")
        return {
            "success": False,
            "error": "Método no implementado"
        }
