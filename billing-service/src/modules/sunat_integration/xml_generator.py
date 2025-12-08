"""
XML UBL 2.1 Generator for SUNAT
Generador de XML según estándar UBL 2.1 de SUNAT
"""
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
from lxml import etree
from loguru import logger


class UBLXMLGenerator:
    """Generador de XML UBL 2.1 para comprobantes electrónicos"""

    # Namespaces UBL 2.1
    NAMESPACES = {
        None: "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "ccts": "urn:un:unece:uncefact:documentation:2",
        "ds": "http://www.w3.org/2000/09/xmldsig#",
        "ext": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
        "qdt": "urn:oasis:names:specification:ubl:schema:xsd:QualifiedDatatypes-2",
        "sac": "urn:sunat:names:specification:ubl:peru:schema:xsd:SunatAggregateComponents-1",
        "udt": "urn:un:unece:uncefact:data:specification:UnqualifiedDataTypesSchemaModule:2",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    }

    # Catálogos SUNAT
    TIPO_DOCUMENTO = {
        "FACTURA": "01",
        "BOLETA": "03",
        "NOTA_CREDITO": "07",
        "NOTA_DEBITO": "08",
    }

    TIPO_DOC_IDENTIDAD = {
        "DNI": "1",
        "RUC": "6",
        "CE": "4",
        "PASAPORTE": "7",
    }

    MONEDA = {
        "SOLES": "PEN",
        "DOLARES": "USD",
    }

    TIPO_IGV = {
        "GRAVADO": "10",  # Gravado - Operación Onerosa
        "EXONERADO": "20",
        "INAFECTO": "30",
    }

    def __init__(self):
        """Inicializar generador"""
        pass

    def generate_invoice(
        self,
        invoice_data: Dict,
        company_data: Dict,
        client_data: Dict,
        items: List[Dict],
    ) -> str:
        """
        Generar XML de Factura o Boleta (UBL 2.1)

        Args:
            invoice_data: Datos del comprobante (serie, número, fecha, tipo)
            company_data: Datos del emisor (RUC, razón social, dirección)
            client_data: Datos del cliente (tipo doc, número, razón social)
            items: Lista de items/servicios del comprobante

        Returns:
            XML como string
        """
        logger.info(f"Generando XML UBL 2.1 para {invoice_data.get('serie')}-{invoice_data.get('numero')}")

        # Crear elemento raíz <Invoice>
        root = etree.Element(
            "Invoice",
            nsmap=self.NAMESPACES,
        )
        root.set("{http://www.w3.org/2001/XMLSchema-instance}schemaLocation",
                 "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2")

        # UBLExtensions (para firma digital)
        self._add_ubl_extensions(root)

        # UBLVersionID
        self._add_element(root, "cbc:UBLVersionID", "2.1")

        # CustomizationID (versión de formato SUNAT)
        self._add_element(root, "cbc:CustomizationID", "2.0")

        # ID del comprobante (Serie-Número)
        serie = invoice_data.get("serie", "F001")
        numero = str(invoice_data.get("numero", 1)).zfill(8)
        self._add_element(root, "cbc:ID", f"{serie}-{numero}")

        # IssueDate (fecha de emisión)
        fecha_emision = invoice_data.get("fecha_emision", datetime.now())
        if isinstance(fecha_emision, str):
            fecha_emision = datetime.fromisoformat(fecha_emision.replace("Z", "+00:00"))
        self._add_element(root, "cbc:IssueDate", fecha_emision.strftime("%Y-%m-%d"))

        # IssueTime (hora de emisión)
        self._add_element(root, "cbc:IssueTime", fecha_emision.strftime("%H:%M:%S"))

        # InvoiceTypeCode (01=Factura, 03=Boleta)
        tipo_comprobante = invoice_data.get("tipo_comprobante", "01")
        self._add_element(root, "cbc:InvoiceTypeCode", tipo_comprobante,
                         listID="0101")  # Catálogo 01

        # DocumentCurrencyCode (PEN, USD)
        moneda = invoice_data.get("moneda", "PEN")
        self._add_element(root, "cbc:DocumentCurrencyCode", moneda)

        # Signature (firma digital - placeholder)
        self._add_signature_placeholder(root, company_data)

        # AccountingSupplierParty (Emisor - Empresa)
        self._add_supplier_party(root, company_data)

        # AccountingCustomerParty (Cliente/Receptor)
        self._add_customer_party(root, client_data)

        # TaxTotal (Total de impuestos - IGV)
        self._add_tax_total(root, invoice_data, items)

        # LegalMonetaryTotal (Totales del comprobante)
        self._add_legal_monetary_total(root, invoice_data)

        # InvoiceLine (Líneas/Items del comprobante)
        for idx, item in enumerate(items, start=1):
            self._add_invoice_line(root, idx, item, moneda)

        # Convertir a string XML
        xml_string = etree.tostring(
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding="UTF-8",
        ).decode("utf-8")

        logger.info(f"XML generado exitosamente: {len(xml_string)} bytes")
        return xml_string

    def _add_ubl_extensions(self, parent):
        """Añadir UBLExtensions (para firma digital)"""
        ext = etree.SubElement(parent, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions")
        ext_elem = etree.SubElement(ext, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtension")
        ext_content = etree.SubElement(ext_elem, "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent")
        # Aquí irá la firma digital (se añade después con signxml)
        return ext_content

    def _add_signature_placeholder(self, parent, company_data: Dict):
        """Añadir placeholder para firma digital"""
        nsmap_cac = {"cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"}
        nsmap_cbc = {"cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"}

        sig = etree.SubElement(parent, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}Signature")

        sig_id = etree.SubElement(sig, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        sig_id.text = company_data.get("ruc", "")

        sig_party = etree.SubElement(sig, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}SignatoryParty")
        party_id = etree.SubElement(sig_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyIdentification")
        party_id_val = etree.SubElement(party_id, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}ID")
        party_id_val.text = company_data.get("ruc", "")

        party_name = etree.SubElement(sig_party, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}PartyName")
        party_name_val = etree.SubElement(party_name, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}Name")
        party_name_val.text = company_data.get("razon_social", "")

        digital_sig = etree.SubElement(sig, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}DigitalSignatureAttachment")
        ext_ref = etree.SubElement(digital_sig, "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}ExternalReference")
        uri = etree.SubElement(ext_ref, "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}URI")
        uri.text = f"#{company_data.get('ruc', '')}"

    def _qname(self, prefix: str, localname: str) -> str:
        """Helper para crear QNames con namespace"""
        ns = self.NAMESPACES.get(prefix)
        if ns:
            return f"{{{ns}}}{localname}"
        return localname

    def _add_supplier_party(self, parent, company_data: Dict):
        """Añadir datos del emisor (empresa)"""
        supplier = etree.SubElement(parent, self._qname("cac", "AccountingSupplierParty"))
        party = etree.SubElement(supplier, self._qname("cac", "Party"))

        # Party Identification (RUC)
        party_id = self._create_element(party, "cac:PartyIdentification")
        self._add_element(party_id, "cbc:ID", company_data.get("ruc", ""),
                         schemeID="6")  # 6=RUC

        # Party Name
        party_name = self._create_element(party, "cac:PartyName")
        self._add_element(party_name, "cbc:Name", company_data.get("nombre_comercial", ""))

        # Postal Address (dirección)
        address = self._create_element(party, "cac:PostalAddress")
        self._add_element(address, "cbc:StreetName", company_data.get("direccion", ""))
        self._add_element(address, "cbc:CityName", company_data.get("ciudad", "LIMA"))
        self._add_element(address, "cbc:CountrySubentity", company_data.get("departamento", "LIMA"))
        self._add_element(address, "cbc:District", company_data.get("distrito", "LIMA"))

        country = self._create_element(address, "cac:Country")
        self._add_element(country, "cbc:IdentificationCode", "PE")

        # Party Legal Entity
        legal = self._create_element(party, "cac:PartyLegalEntity")
        self._add_element(legal, "cbc:RegistrationName", company_data.get("razon_social", ""))

    def _add_customer_party(self, parent, client_data: Dict):
        """Añadir datos del cliente"""
        customer = self._create_element(parent, "cac:AccountingCustomerParty")
        party = self._create_element(customer, "cac:Party")

        # Party Identification
        party_id = self._create_element(party, "cac:PartyIdentification")
        tipo_doc = client_data.get("tipo_documento", "6")  # 6=RUC, 1=DNI
        self._add_element(party_id, "cbc:ID", client_data.get("numero_documento", ""),
                         schemeID=tipo_doc)

        # Party Legal Entity
        legal = self._create_element(party, "cac:PartyLegalEntity")
        nombre_cliente = client_data.get("razon_social") or client_data.get("nombres_completos", "")
        self._add_element(legal, "cbc:RegistrationName", nombre_cliente)

    def _add_tax_total(self, parent, invoice_data: Dict, items: List[Dict]):
        """Añadir totales de impuestos (IGV)"""
        tax_total = self._create_element(parent, "cac:TaxTotal")

        # TaxAmount (monto total de IGV)
        igv_total = invoice_data.get("igv", Decimal("0.00"))
        self._add_element(tax_total, "cbc:TaxAmount", f"{igv_total:.2f}",
                         currencyID=invoice_data.get("moneda", "PEN"))

        # TaxSubtotal (detalle de IGV)
        subtotal = self._create_element(tax_total, "cac:TaxSubtotal")

        base_imponible = invoice_data.get("subtotal", Decimal("0.00"))
        self._add_element(subtotal, "cbc:TaxableAmount", f"{base_imponible:.2f}",
                         currencyID=invoice_data.get("moneda", "PEN"))
        self._add_element(subtotal, "cbc:TaxAmount", f"{igv_total:.2f}",
                         currencyID=invoice_data.get("moneda", "PEN"))

        # TaxCategory
        category = self._create_element(subtotal, "cac:TaxCategory")
        self._add_element(category, "cbc:ID", "S")  # S = Sujeto a IGV

        # TaxScheme (IGV)
        scheme = self._create_element(category, "cac:TaxScheme")
        self._add_element(scheme, "cbc:ID", "1000")  # Catálogo 05: 1000=IGV
        self._add_element(scheme, "cbc:Name", "IGV")
        self._add_element(scheme, "cbc:TaxTypeCode", "VAT")

    def _add_legal_monetary_total(self, parent, invoice_data: Dict):
        """Añadir totales monetarios"""
        monetary_total = self._create_element(parent, "cac:LegalMonetaryTotal")

        moneda = invoice_data.get("moneda", "PEN")
        subtotal = invoice_data.get("subtotal", Decimal("0.00"))
        total = invoice_data.get("total", Decimal("0.00"))

        # LineExtensionAmount (suma de valores de venta)
        self._add_element(monetary_total, "cbc:LineExtensionAmount", f"{subtotal:.2f}",
                         currencyID=moneda)

        # TaxInclusiveAmount (total con impuestos)
        self._add_element(monetary_total, "cbc:TaxInclusiveAmount", f"{total:.2f}",
                         currencyID=moneda)

        # PayableAmount (importe total a pagar)
        self._add_element(monetary_total, "cbc:PayableAmount", f"{total:.2f}",
                         currencyID=moneda)

    def _add_invoice_line(self, parent, line_id: int, item: Dict, moneda: str):
        """Añadir línea de item/servicio"""
        line = self._create_element(parent, "cac:InvoiceLine")

        # ID de línea
        self._add_element(line, "cbc:ID", str(line_id))

        # InvoicedQuantity (cantidad)
        cantidad = item.get("cantidad", 1)
        self._add_element(line, "cbc:InvoicedQuantity", str(cantidad),
                         unitCode=item.get("unidad_medida", "NIU"))  # NIU=Unidad

        # LineExtensionAmount (valor de venta de la línea)
        valor_unitario = float(item.get("valor_unitario", 0))
        valor_venta = valor_unitario * cantidad
        self._add_element(line, "cbc:LineExtensionAmount", f"{valor_venta:.2f}",
                         currencyID=moneda)

        # PricingReference (precio unitario referencial)
        pricing_ref = self._create_element(line, "cac:PricingReference")
        alt_price = self._create_element(pricing_ref, "cac:AlternativeConditionPrice")
        precio_unitario = float(item.get("precio_unitario", 0))
        self._add_element(alt_price, "cbc:PriceAmount", f"{precio_unitario:.2f}",
                         currencyID=moneda)
        self._add_element(alt_price, "cbc:PriceTypeCode", "01")  # 01=Precio unitario

        # TaxTotal (IGV de la línea)
        tax_total = self._create_element(line, "cac:TaxTotal")
        igv_linea = float(item.get("igv", 0))
        self._add_element(tax_total, "cbc:TaxAmount", f"{igv_linea:.2f}",
                         currencyID=moneda)

        # TaxSubtotal
        tax_subtotal = self._create_element(tax_total, "cac:TaxSubtotal")
        self._add_element(tax_subtotal, "cbc:TaxableAmount", f"{valor_venta:.2f}",
                         currencyID=moneda)
        self._add_element(tax_subtotal, "cbc:TaxAmount", f"{igv_linea:.2f}",
                         currencyID=moneda)

        tax_category = self._create_element(tax_subtotal, "cac:TaxCategory")
        self._add_element(tax_category, "cbc:Percent", "18.00")  # IGV 18%
        self._add_element(tax_category, "cbc:TaxExemptionReasonCode", "10")  # Gravado

        tax_scheme = self._create_element(tax_category, "cac:TaxScheme")
        self._add_element(tax_scheme, "cbc:ID", "1000")  # IGV
        self._add_element(tax_scheme, "cbc:Name", "IGV")
        self._add_element(tax_scheme, "cbc:TaxTypeCode", "VAT")

        # Item (descripción del producto/servicio)
        item_elem = self._create_element(line, "cac:Item")
        self._add_element(item_elem, "cbc:Description", item.get("descripcion", ""))

        sellers_id = self._create_element(item_elem, "cac:SellersItemIdentification")
        self._add_element(sellers_id, "cbc:ID", item.get("codigo", ""))

        # Price (precio unitario sin IGV)
        price = self._create_element(line, "cac:Price")
        self._add_element(price, "cbc:PriceAmount", f"{item.get('valor_unitario', 0):.2f}",
                         currencyID=moneda)

    def _create_element(self, parent, tag: str):
        """Crear elemento hijo con namespace"""
        if ":" in tag:
            prefix, localname = tag.split(":", 1)
            full_tag = self._qname(prefix, localname)
        else:
            full_tag = tag
        return etree.SubElement(parent, full_tag)

    def _add_element(self, parent, tag: str, text: str, **attribs):
        """Crear elemento con texto y atributos"""
        if ":" in tag:
            prefix, localname = tag.split(":", 1)
            full_tag = self._qname(prefix, localname)
        else:
            full_tag = tag
        elem = etree.SubElement(parent, full_tag)
        elem.text = text
        for key, value in attribs.items():
            elem.set(key, value)
        return elem
