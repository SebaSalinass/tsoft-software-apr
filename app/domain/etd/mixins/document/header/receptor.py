from dataclasses import dataclass, field
from typing import Optional

import lxml.etree as ET

from app.domain.shared.mixins.address import AddressMixin


@dataclass
class ReceptorMixin:

    rut: str
    name: str

    business_activity: Optional[str] = field(repr=False, default=None)
    address: Optional[AddressMixin] = field(repr=False, default=None)
    internal_id: Optional[str] = field(repr=False, default=None)
    phones: Optional[list[str]] = field(repr=False, default=None)

    def lxml_element(self) -> ET.Element:

        root = ET.Element('Receptor')
        rut = ET.SubElement(root, 'RUTRecep')
        rut.text = self.rut

        if self.internal_id:
            internal_id = ET.SubElement(root, 'CdgIntRecep')
            internal_id.text = self.internal_id

        name = ET.SubElement(root, 'RznSocRecep')
        name.text = self.name

        if self.business_activity:
            business_activity = ET.SubElement(root, 'GiroRecep')
            business_activity.text = self.business_activity

        if self.address:
            address = ET.SubElement(root, 'DirRecep')
            address.text = self.address.address
            commune = ET.SubElement(root, 'CmnaRecep')
            commune.text = self.address.commune
            city = ET.SubElement(root, 'CiudadRecep')
            city.text = self.address.city

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'ReceptorMixin':

        rut = element.find(prefix+'RUTRecep').text
        name = element.find(prefix+'RznSocRecep').text

        internal_id = element.find(prefix+'CdgIntRecep')
        if internal_id is not None:
            internal_id = internal_id.text

        business_activity = element.find(prefix+'GiroRecep')
        if business_activity is not None:
            business_activity = business_activity.text

        commune = element.find(prefix+'CmnaRecep')
        if commune is not None:
            commune = commune.text

        city = element.find(prefix+'CiudadRecep')
        if city is not None:
            city = city.text

        address = element.find(prefix+'DirRecep')
        if address is not None:
            address = address.text

        obj_address = None
        if address or commune or city:
            obj_address = AddressMixin(address, city, commune)

        phones = element.findall(prefix+'Telefono')
        if phones is not None:
            phones = [phone.text for phone in phones]

        return cls(rut, name, business_activity, obj_address, internal_id, phones)
