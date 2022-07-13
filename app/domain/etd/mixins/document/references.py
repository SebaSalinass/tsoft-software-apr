from dataclasses import dataclass, field
from typing import Optional

import lxml.etree as ET
from arrow import Arrow, get

from ...constants.document import DocumentType, ReferenceCode

@dataclass
class ReferenceMixin:

    line: int
    doc_type: Optional[DocumentType]

    folio_ref: Optional[int]
    date_ref: Optional[Arrow]
    code_ref: Optional[ReferenceCode]
    reason_ref: Optional[str] = field(repr=False, default=None)

    def lxml_element(self) -> ET.Element:

        root = ET.Element('Referencia')
        ref_index = ET.SubElement(root, 'NroLinRef')
        ref_index.text = str(self.line)

        if self.doc_type:
            doc_type = ET.SubElement(root, 'TpoDocRef')
            doc_type.text = str(self.doc_type)

        if self.folio_ref:
            folio = ET.SubElement(root, 'FolioRef')
            folio.text = str(self.folio_ref)

        if self.date_ref:
            date_ref = ET.SubElement(root, 'FchRef')
            date_ref.text = self.date_ref.format('YYYY-MM-DD')

        if self.code_ref:
            code_ref = ET.SubElement(root, 'CodRef')
            code_ref.text = str(self.code_ref)

        if self.reason_ref:
            reason_ref = ET.SubElement(root, 'RazonRef')
            reason_ref.text = self.reason_ref

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'ReferenceMixin':

        line = element.find(prefix + 'NroLinRef')
        doc_type = element.find(prefix + 'TpoDocRef')
        folio_ref = element.find(prefix + 'FolioRef')
        date_ref = element.find(prefix + 'FchRef')
        code_ref = element.find(prefix + 'CodRef')
        reason_ref = element.find(prefix + 'RazonRef')

        line = int(line.text)
        doc_type = DocumentType(
            int(doc_type.text)) if doc_type.text != 'SET' else DocumentType.SET_PRUEBA
        folio_ref = int(folio_ref.text)
        date_ref = get(date_ref.text)
        code_ref = code_ref.text if code_ref is not None else None
        reason_ref = reason_ref.text if reason_ref is not None else None

        return cls(line, doc_type, folio_ref, date_ref, code_ref, reason_ref)
