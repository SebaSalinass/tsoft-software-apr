from dataclasses import dataclass, field
from typing import Optional, Union

import lxml.etree as ET

from ...constants.document import ExemptionIndex, MeasurementType


@dataclass
class DetailMixin:

    line: int 
    item_name: str

    item_quantity: Optional[Union[float, int]] = field(repr=False, default=0)
    item_unit_price: Optional[Union[float, int]] = field(repr=False, default=0)

    discount_percentage: float = field(repr=False, default=0.0)
    discount_amount: int = field(repr=False, default=0)

    surcharge_percentage: float = field(repr=False, default=0.0)
    surcharge_amount: int = field(repr=False, default=0)
    
    item_description: Optional[str] = field(repr=False, default=None)
    item_measurement: Optional[MeasurementType] = field(repr=False, default=None)
    exemption_index: Optional[ExemptionIndex] = field(repr=False, default=None)

    discount_applied: bool = field(repr=False, default=False)
    surcharge_applied: bool = field(repr=False, default=False)
    _item_amount: int = field(repr=False, default=0)

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'DetailMixin':

        detail_dict = {
            'line': int(element.find(prefix+'NroLinDet').text),
            'item_name': element.find(prefix+'NmbItem').text,
        }

        exemption_index = element.find(prefix+'IndExe')
        if exemption_index is not None:
            detail_dict['exemption_index'] = ExemptionIndex(int(exemption_index.text))

        item_description = element.find(prefix+'DscItem')
        if item_description is not None:
            detail_dict['item_description'] = item_description.text

        item_quantity = element.find(prefix+'QtyItem')
        if item_quantity is not None:
            detail_dict['item_quantity'] = float(item_quantity.text)

        item_measurement = element.find(prefix+'UnmdItem')
        if item_measurement is not None:
            try:
                detail_dict['item_measurement'] = MeasurementType(int(item_measurement.text))
            except:
                detail_dict['item_measurement'] = item_measurement.text

        item_unit_price = element.find(prefix+'PrcItem')
        if item_unit_price is not None:
            detail_dict['item_unit_price'] = float(item_unit_price.text)

        discount_percentage = element.find(prefix+'DescuentoPct')
        if discount_percentage is not None:
            detail_dict['discount_percentage'] = float(discount_percentage.text)

        discount_amount = element.find(prefix+'DescuentoMonto')
        if discount_amount is not None:
            detail_dict['discount_amount'] = int(discount_amount.text)

        surcharge_percentage = element.find(prefix+'RecargoPct')
        if surcharge_percentage is not None:
            detail_dict['surcharge_percentage'] = float(surcharge_percentage.text)

        surcharge_amount = element.find(prefix+'RecargoMonto')
        if surcharge_amount is not None:
            detail_dict['surcharge_amount'] = int(surcharge_amount.text)

        _item_amount = element.find(prefix+'MontoItem')
        if _item_amount is not None:
            detail_dict['_item_amount'] = int(_item_amount.text)

        return cls(**detail_dict)

    @property
    def item_amount(self) -> int:
        if self._item_amount:
            return self._item_amount
        return int(self.item_unit_price * self.item_quantity) - self.discount_amount + self.surcharge_amount

    def apply_discount_amount(self, amount: int) -> int:

        if amount <= 0:
            raise ValueError('Discount amount must be greater than 0')

        if self.discount_applied:
            self.undo_discount()

        self.discount_amount = amount
        self.discount_applied = True

        return self.item_amount

    def apply_discount_pct(self, pct: float) -> int:
        if not (0 < pct <= 100):
            raise ValueError(
                'Discount percentage can not be less or equal 0')

        if self.discount_applied:
            self.undo_discount()

        self.discount_percentage = pct
        self.discount_amount = int(
            round((self.item_amount * self.discount_percentage / 100), 0))
        self.discount_applied = True

        return self.item_amount

    def apply_surcharge_amount(self, amount: int) -> int:

        if amount <= 0:
            raise ValueError('Surcharge amount must be greater than 0')

        if self.surcharge_applied:
            self.undo_surcharge()

        self.surcharge_amount = amount
        self.surcharge_applied = True
        return self.item_amount

    def apply_surcharge_pct(self, pct: float) -> int:
        if not (0 < pct <= 100):
            raise ValueError(
                'Surcharge percentage can not be less or equal 0')

        if self.surcharge_applied:
            self.undo_surcharge()

        self.surcharge_percentage = pct
        self.surcharge_amount = int(
            round((self.item_amount * self.surcharge_percentage / 100), 0))
        self.surcharge_applied = True

        return self.item_amount

    def undo_discount(self) -> None:

        self.discount_amount = 0
        self.discount_percentage = 0.0
        self.discount_applied = False

    def undo_surcharge(self) -> None:

        self.surcharge_amount = 0
        self.surcharge_percentage = 0.0
        self.surcharge_applied = False

    def lxml_element(self) -> ET.Element:
        root = ET.Element('Detalle')

        index = ET.SubElement(root, 'NroLinDet')
        index.text = str(self.line)

        if self.exemption_index:
            exemption_index = ET.SubElement(root, 'IndExe')
            exemption_index.text = str(self.exemption_index)

        item_name = ET.SubElement(root, 'NmbItem')
        item_name.text = self.item_name

        if self.item_description:
            item_description = ET.SubElement(root, 'DscItem')
            item_description.text = self.item_description

        if self.item_quantity:
            item_quantity = ET.SubElement(root, 'QtyItem')
            item_quantity.text = str(round(self.item_quantity, 2))

        if self.item_measurement:
            item_measurement = ET.SubElement(root, 'UnmdItem')
            item_measurement.text = str(self.item_measurement)

        if self.item_unit_price:
            item_price = ET.SubElement(root, 'PrcItem')
            item_price.text = str(round(self.item_unit_price, 2))

        if self.discount_percentage:
            discount_percentage = ET.SubElement(root, 'DescuentoPct')
            discount_percentage.text = str(self.discount_percentage)

        if self.discount_amount:
            discount_amount = ET.SubElement(root, 'DescuentoMonto')
            discount_amount.text = str(self.discount_amount)

        if self.surcharge_percentage:
            surcharge_percentage = ET.SubElement(root, 'RecargoPct')
            surcharge_percentage.text = str(self.surcharge_percentage)

        if self.surcharge_amount:
            surcharge_amount = ET.SubElement(root, 'RecargoMonto')
            surcharge_amount.text = str(self.surcharge_amount)

        item_amount = ET.SubElement(root, 'MontoItem')
        item_amount.text = str(self.item_amount)

        return root
