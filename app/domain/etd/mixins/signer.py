from dataclasses import dataclass, field
from typing import Optional
from io import BytesIO
import base64

from lxml import etree as ET
from arrow import Arrow, utcnow, get
from cryptography.hazmat.primitives.serialization import pkcs12
import xmlsec

from ..constants.signer import SignerState

@dataclass
class SignerMixin:
    
    serial_number: int
    valid_from: Arrow
    valid_to: Arrow

    active_from: Optional[Arrow] = field(repr=False, default=None)
    active_to: Optional[Arrow] = field(repr=False, default=None)
    state: SignerState = field(repr=False, default=SignerState.INACTIVE)
    
    _cert_data: bytes = field(default=None, repr=False)
    _cert_password: bytes = field(default=None, repr=False)
        
    @property
    def time_remaining(self) -> str:
        return self.valid_to.humanize(granularity=["auto"], locale='es', only_distance=True)

    @property
    def is_valid(self) -> bool:
        return utcnow() < self.valid_to

    def activate(self) -> None:
        assert self.state == SignerState.INACTIVE
        self.state = SignerState.ACTIVE
        self.active_from == utcnow()

    def disable(self) -> None:
        assert self.state == SignerState.ACTIVE
        self.state = SignerState.DISABLED
        self.active_to = utcnow()
    
    @property
    def xmlsec_key(self) -> xmlsec.Key:
        password = base64.b64decode(self._cert_password).decode('utf-8')
        return xmlsec.Key.from_memory(self._cert_data, xmlsec.constants.KeyDataFormatPkcs12, password)

    def sign_element(self, element: ET.Element, id_node: str = None) -> bytes:

        data = BytesIO()
        data.write(ET.tostring(element, pretty_print=True, doctype='<?xml version="1.0" encoding="ISO-8859-1"?>'))
        data.seek(0)

        template = ET.parse(data).getroot()
        signature_node = xmlsec.tree.find_child(template, xmlsec.constants.NodeSignature)
        ctx = xmlsec.SignatureContext()

        if id_node:
            ctx.register_id(template.find(id_node), id_attr='ID')

        ctx.key = self.xmlsec_key
        ctx.sign(signature_node)

        return ET.tostring(template)

    def sign_element_seed(self, element: ET.Element, id_node: str = None) -> bytes:

        data = BytesIO()
        data.write(ET.tostring(element, pretty_print=True, doctype='<?xml version="1.0" encoding="UTF-8"?>'))
        data.seek(0)

        template = ET.parse(data).getroot()
        signature_node = xmlsec.tree.find_child(template, xmlsec.constants.NodeSignature)
        ctx = xmlsec.SignatureContext()

        if id_node:
            ctx.register_id(template.find(id_node), id_attr='ID')

        ctx.key = self.xmlsec_key
        ctx.sign(signature_node)

        return ET.tostring(template, pretty_print=True, xml_declaration=True).decode('utf-8')

    def sign_seed_lxml_element(self, seed: str) -> bytes:

        root = ET.Element('getToken')
        item = ET.SubElement(root, 'item')
        seed_element = ET.SubElement(item, 'Semilla')
        seed_element.text = seed

        root.insert(1, self.__signature_node())

        signed = self.sign_element_seed(root)
        self.last_signed = signed

        return signed

    def sign_seed_to_xml_file(self, seed: str, filename: str) -> None:
        with open(f'{filename}.xml', 'wb') as xml_output:
            xml_element = self.sign_seed_lxml_element(seed)
            xml_output.write(xml_element)

    def _verify_signature(self, file_path: str) -> None:
        ''' file path or file like object'''
        template = ET.parse(file_path).getroot()
        xmlsec.tree.add_ids(template, ['ID'])

        signature_node = xmlsec.tree.find_child(template, xmlsec.constants.NodeSignature)
        # Create a digital signature context (no key manager is needed).
        ctx = xmlsec.SignatureContext()
        ctx.key = self.xmlsec_key
        ctx.verify(signature_node)
        return None

    def __signature_node(self) -> ET.Element:

        root = ET.Element('Signature', xmlns='http://www.w3.org/2000/09/xmldsig#')

        signed_info = ET.SubElement(root, 'SignedInfo')
        ET.SubElement(signed_info, 'CanonicalizationMethod', attrib={'Algorithm': 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'})
        ET.SubElement(signed_info, 'SignatureMethod', attrib={'Algorithm': 'http://www.w3.org/2000/09/xmldsig#rsa-sha1'})
        reference = ET.SubElement(signed_info, 'Reference', attrib={'URI': ''})
        transforms = ET.SubElement(reference, 'Transforms')
        ET.SubElement(transforms, 'Transform', attrib={'Algorithm': 'http://www.w3.org/2000/09/xmldsig#enveloped-signature'})
        ET.SubElement(reference, 'DigestMethod', attrib={'Algorithm': 'http://www.w3.org/2000/09/xmldsig#sha1'})
        ET.SubElement(reference, 'DigestValue')
        ET.SubElement(root, 'SignatureValue')
        key_info = ET.SubElement(root, 'KeyInfo')
        ET.SubElement(key_info, 'KeyValue')

        x509 = ET.SubElement(key_info, 'X509Data')
        ET.SubElement(x509, 'X509Certificate')

        return root

    @classmethod
    def from_cert_data(cls, cert_data: bytes, password: str) -> 'SignerMixin':

        if hasattr(cert_data, 'read'):
            cert_data = cert_data.read()


        password = bytes(password, encoding='utf-8')
        _, cert, _ = pkcs12.load_key_and_certificates(cert_data, password)

        not_after = get(cert.not_valid_after)
        not_before = get(cert.not_valid_before)

        signer_dict = {
            'serial_number': cert.serial_number,
            'valid_from': not_before,
            'valid_to': not_after,
            '_cert_data': cert_data,
            '_cert_password': base64.b64encode(password),            

        }

        return cls(**signer_dict)