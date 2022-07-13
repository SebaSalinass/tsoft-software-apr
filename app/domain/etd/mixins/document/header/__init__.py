from dataclasses import dataclass, field
import lxml.etree as ET

from typing import Union
from arrow import Arrow

from ....constants.document import DocumentType
from .id import IDMixin
from .issuer import IssuerMixin
from .receptor import ReceptorMixin
from .totals import TotalsMixin


@dataclass
class HeaderMixin:

    doc_id: IDMixin
    issuer: IssuerMixin = field(repr=False)
    receptor: ReceptorMixin = field(repr=False)
    totals: TotalsMixin = field(repr=False, default_factory=TotalsMixin)

    @property
    def date_from(self) -> Union[Arrow, None]:
        return self.doc_id.date_from

    @property
    def date_to(self) -> Union[Arrow, None]:
        return self.doc_id.date_to

    @property
    def date_expiration(self) -> Union[Arrow, None]:
        return self.doc_id.date_expiration

    def lxml_element(self) -> ET.Element:

        voucher = (self.doc_id.doc_type in [
                   DocumentType.BOLETA_ELECTRÓNICA_EXENTA, DocumentType.BOLETA_ELECTRÓNICA])

        root = ET.Element('Encabezado')
        root.insert(0, self.doc_id.lxml_element())
        root.insert(1, self.issuer.lxml_element(voucher))
        root.insert(2, self.receptor.lxml_element())
        root.insert(3, self.totals.lxml_element(voucher))

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'HeaderMixin':

        doc_id = IDMixin.from_xml_element(element.find(prefix+'IdDoc'), prefix)
        issuer = IssuerMixin.from_xml_element(
            element.find(prefix+'Emisor'), prefix)
        receptor = ReceptorMixin.from_xml_element(
            element.find(prefix+'Receptor'), prefix)
        totals = TotalsMixin.from_xml_element(
            element.find(prefix+'Totales'), prefix)

        return cls(doc_id, issuer, receptor, totals)
