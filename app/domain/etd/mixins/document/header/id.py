from dataclasses import dataclass, field
from typing import Optional

from arrow import Arrow, utcnow, get
import lxml.etree as ET

from ....constants.document import DocumentType, ServiceIndex


@dataclass
class IDMixin:

    doc_type: DocumentType
    folio: int
    date_emited: Arrow = field(default_factory=utcnow)

    service_index: Optional[ServiceIndex] = field(repr=False, default=ServiceIndex.FACTURA_SERVICIOS)

    date_from: Optional[Arrow] = field(repr=False, default=None)
    date_to: Optional[Arrow] = field(repr=False, default=None)
    date_expiration: Optional[Arrow] = field(repr=False, default=None)

    def lxml_element(self) -> ET.Element:

        root = ET.Element('IdDoc')
        doc_type = ET.SubElement(root, 'TipoDTE')
        doc_type.text = str(self.doc_type)

        folio = ET.SubElement(root, 'Folio')
        folio.text = str(self.folio)

        date_emited = ET.SubElement(root, 'FchEmis')
        date_emited.text = self.date_emited.format('YYYY-MM-DD')

        if self.service_index:
            service_index = ET.SubElement(root, 'IndServicio')
            service_index.text = str(self.service_index)
        if self.date_from:
            date_from = ET.SubElement(root, 'PeriodoDesde')
            date_from.text = self.date_from.format('YYYY-MM-DD')
        if self.date_to:
            date_to = ET.SubElement(root, 'PeriodoHasta')
            date_to.text = self.date_to.format('YYYY-MM-DD')
        if self.date_expiration:
            date_expiration = ET.SubElement(root, 'FchVenc')
            date_expiration.text = self.date_expiration.format('YYYY-MM-DD')

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'IDMixin':

        doc_type = DocumentType(int(element.find(prefix + 'TipoDTE').text))
        folio = int(element.find(prefix+'Folio').text)
        date_emited = get(element.find(prefix+'FchEmis').text)

        service_index = element.find(prefix + 'IndServicio')
        if service_index is not None:
            service_index = ServiceIndex(int(service_index.text))

        date_from = element.find(prefix + 'PeriodoDesde')
        if date_from is not None:
            date_from = get(date_from.text)

        date_to = element.find(prefix + 'PeriodoHasta')
        if date_to is not None:
            date_to = get(date_to.text)

        date_expiration = element.find(prefix + 'FchVenc')
        if date_expiration is not None:
            date_expiration = get(date_expiration.text)

        return cls(doc_type, folio, date_emited, service_index=service_index, date_from=date_from, date_to=date_to, date_expiration=date_expiration)