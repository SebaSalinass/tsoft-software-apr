from dataclasses import dataclass, field
from typing import Optional, Union

import lxml.etree as ET

from ...constants.document import MovementType, ValueType, ExemptionIndex


@dataclass
class GlobalDiscountSurchargeMixin:

    line: int
    value_type: ValueType
    movement_type: MovementType
    value: Union[int, float]
    comment: Optional[str] = field(repr=False, default=None)
    exemption_index: Optional[ExemptionIndex] = field(repr=False, default=None)

    def lxml_element(self) -> ET.Element:

        root = ET.Element('DscRcgGlobal')
        line = ET.SubElement(root, 'NroLinDR')
        line.text = str(self.line)

        mov_type = ET.SubElement(root, 'TpoMov')
        mov_type.text = str(self.movement_type)

        if self.comment:
            comment = ET.SubElement(root, 'GlosaDR')
            comment.text = self.comment

        value_type = ET.SubElement(root, 'TpoValor')
        value_type.text = str(self.value_type)

        if isinstance(self.value, float):
            self.value = round(self.value, 2)

        value = ET.SubElement(root, 'ValorDR')
        value.text = str(self.value)

        if self.exemption_index:
            exemption_index = ET.SubElement(root, 'IndExeDR')
            exemption_index.text = str(self.exemption_index)

        return root

    def apply_discount_surcharge(self, amount: int) -> int:

        if self.movement_type == MovementType.DESCUENTO:
            if self.value_type == ValueType.PORCENTAJE:
                return amount - int(round((amount * self.value / 100), 0))
            else:
                return amount - int(self.value)
        else:
            if self.value_type == ValueType.PORCENTAJE:
                return amount + int(round((amount * self.value / 100), 0))
            else:
                return amount + int(self.value)

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'GlobalDiscountSurchargeMixin':

        exemption_index = element.find(prefix+'IndExeDR')
        comment = element.find(prefix+'GlosaDR')

        reference_dict = {
            'line': int(element.find(prefix+'NroLinDR').text),
            'value_type': ValueType(element.find(prefix+'TpoValor').text),
            'movement_type': MovementType(element.find(prefix+'TpoMov').text),
            'value': float(element.find(prefix+'ValorDR').text),
            'exemption_index': ExemptionIndex[exemption_index.text] if exemption_index is not None else None,
            'comment': comment.text if comment is not None else None
        }

        return cls(**reference_dict)
