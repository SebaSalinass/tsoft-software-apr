from dataclasses import dataclass, field

from ...shared.mixins.base import BaseMixin
from .document import DocumentMixin
from .signer import SignerMixin
from .signable import SignableMixin

import lxml.etree as ET

@dataclass
class ETDMixin(BaseMixin, SignableMixin):

    document: DocumentMixin = field(repr=False)
    xml_data: bytes = field(repr=False, default=None)
    sii_sent: bool = field(repr=False, default=False)

    def construct_xml(self, signer: SignerMixin) -> None:

        root = ET.Element('DTE', attrib={'version': '1.0'})
        doc_element = self.document.lxml_element()

        root.insert(0, doc_element)
        root.insert(1, self.get_signature_node(self.document.reference_id))
        self.xml_data = signer.sign_element(root, id_node='Documento')

        return

    def lxml_element(self) -> ET.Element:
        return ET.fromstring(self.xml_data)

    def to_xml_file(self, file_path: str) -> None:

        with open(file_path, 'wb') as xml_file:
            xml_file.write(ET.tostring(
                self.lxml_element(), doctype='<?xml version="1.0" encoding="ISO-8859-1"?>'))

    @classmethod
    def from_data(cls, data: bytes, prefix: str = '') -> 'ETDMixin':

        element = ET.fromstring(data)
        document = DocumentMixin.from_xml_element(
            element.find(prefix + 'Documento'), prefix)    

        return cls(document, xml_data=data)

    @classmethod
    def from_xml_file(cls, file_path: str, prefix: str = '') -> 'ETDMixin':

        with open(file_path, 'rb') as file:
            data = file.read()

        return cls.from_data(data, prefix)
