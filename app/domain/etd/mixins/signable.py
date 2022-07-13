from dataclasses import dataclass, field
from uuid import UUID, uuid4

import lxml.etree as ET

@dataclass
class SignableMixin:

    id: UUID = field(repr=False, default_factory=uuid4, init=False) 

    def get_signature_node(self, doc_id: str = '') -> ET.Element:

        root = ET.Element(
            'Signature', xmlns='http://www.w3.org/2000/09/xmldsig#')

        signed_info = ET.SubElement(root, 'SignedInfo')
        ET.SubElement(signed_info, 'CanonicalizationMethod', attrib={
                      'Algorithm': 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'})
        ET.SubElement(signed_info, 'SignatureMethod', attrib={
                      'Algorithm': 'http://www.w3.org/2000/09/xmldsig#rsa-sha1'})

        reference = ET.SubElement(signed_info, 'Reference', attrib={
                                  'URI': '#' + doc_id})
        transforms = ET.SubElement(reference, 'Transforms')
        ET.SubElement(transforms, 'Transform', attrib={
                      'Algorithm': 'http://www.w3.org/TR/2001/REC-xml-c14n-20010315'})

        ET.SubElement(reference, 'DigestMethod', attrib={
                      'Algorithm': 'http://www.w3.org/2000/09/xmldsig#sha1'})
        ET.SubElement(reference, 'DigestValue')

        ET.SubElement(root, 'SignatureValue')

        key_info = ET.SubElement(root, 'KeyInfo')
        ET.SubElement(key_info, 'KeyValue')

        x509 = ET.SubElement(key_info, 'X509Data')
        ET.SubElement(x509, 'X509Certificate')

        return root
