from dataclasses import dataclass, field
from typing import Optional

import lxml.etree as ET

from app.domain.shared.mixins.address import AddressMixin


@dataclass
class IssuerMixin:

    rut: str
    name: str
    business_activity: str
    business_activity_code: int
    address: AddressMixin

    rut_auth: Optional[str] = field(repr=False, default=None)
    email: Optional[str] = field(repr=False, default=None)
    phones: Optional[list[str]] = field(repr=False, default_factory=list)
    tax_office_name: Optional[str] = field(repr=False, default=None)
    tax_office_code: Optional[int] = field(repr=False, default=None)


    def lxml_element(self, voucher: bool = False) -> ET.Element:

        root = ET.Element('Emisor')

        name_tag = ['RznSoc', 'RznSocEmisor'][voucher]
        business_activity_tag = ['GiroEmis', 'GiroEmisor'][voucher]

        rut = ET.SubElement(root, 'RUTEmisor')
        rut.text = self.rut

        name = ET.SubElement(root, name_tag)
        name.text = self.name

        business_activity = ET.SubElement(root, business_activity_tag)
        business_activity.text = str(self.business_activity).upper()

        if hasattr(self, 'business_activity_code') and not voucher:
            business_act_code = ET.SubElement(root, 'Acteco')
            business_act_code.text = str(self.business_activity_code)

        if self.tax_office_code:
            tax_office_code = ET.SubElement(root, 'CdgSIISucur')
            tax_office_code.text = str(self.tax_office_code)

        address = ET.SubElement(root, 'DirOrigen')
        address.text = self.address.address
        commune = ET.SubElement(root, 'CmnaOrigen')
        commune.text = self.address.commune
        city = ET.SubElement(root, 'CiudadOrigen')
        city.text = self.address.city

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'IssuerMixin':

        rut = element.find(prefix+'RUTEmisor').text

        if element.find(prefix+'RznSoc') is not None:
            name = element.find(prefix+'RznSoc').text
        else:
            name = element.find(prefix+'RznSocEmisor').text

        if element.find(prefix+'GiroEmis') is not None:
            b_activity = element.find(prefix+'GiroEmis').text
        else:
            b_activity = element.find(prefix+'GiroEmisor').text

        b_act_code = element.find(prefix+'Acteco')
        if b_act_code is not None:
            b_act_code = b_act_code.text

        tax_office_code = element.find(prefix+'CdgSIISucur')
        if tax_office_code is not None:
            tax_office_code = int(tax_office_code.text)

        commune = element.find(prefix+'CmnaOrigen')
        if commune is not None:
            commune = commune.text

        city = element.find(prefix+'CiudadOrigen')
        if city is not None:
            city = city.text

        address = element.find(prefix+'DirOrigen')
        if address is not None:
            address = address.text

        phones = element.findall(prefix+'Telefono')
        if phones is not None:
            phones = [phone.text for phone in phones]

        obj_address = AddressMixin(address, city, commune)

        return cls(rut, name, b_activity, b_act_code, address=obj_address,phones=phones, tax_office_code=tax_office_code)