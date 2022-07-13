from typing import Optional, Union

import lxml.etree as ET

from ....constants.document import UnrecoverableTaxCode


class TotalsMixin:

    __net_amount: int = 0
    exent_amount: int = 0
    tax_pct: float = 19.0

    not_billable_amount: Optional[int]

    period_amount: Optional[int]

    outstanding_balance: int = 0
    common_use_tax: bool = False
    unrecoverable_tax: bool = False
    unrecoverable_tax_code: Optional[UnrecoverableTaxCode]

    withheld_tax: bool = False
    withheld_tax_code = 15

    def __init__(self, net_amount: int = 0, exent_amount: int = 0, tax_pct: float = 19.0,
                 not_billable_amount: int = 0, period_amount: int = 0, outstanding_balance: int = 0,
                 common_use_tax: bool = False, unrecoverable_tax: bool = False,
                 unrecoverable_tax_code: Union[UnrecoverableTaxCode,
                                               None] = None,
                 withheld_tax: bool = False, withheld_tax_code: int = 15) -> None:

        self.__net_amount = net_amount
        self.exent_amount = exent_amount
        self.tax_pct = tax_pct
        self.not_billable_amount = not_billable_amount
        self.period_amount = period_amount
        self.outstanding_balance = outstanding_balance
        self.common_use_tax = common_use_tax
        self.unrecoverable_tax = unrecoverable_tax
        self.unrecoverable_tax_code = unrecoverable_tax_code
        self.withheld_tax = withheld_tax
        self.withheld_tax_code = withheld_tax_code

    @property
    def tax_amount(self) -> int:
        from decimal import Decimal, localcontext, ROUND_HALF_UP
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_UP
            tax_amount = int(
                Decimal(self.net_amount * self.tax_pct / 100).to_integral_value())
        return tax_amount

    @property
    def net_amount(self) -> int:
        return self.__net_amount

    @net_amount.setter  # type: ignore
    def net_amount_setter(self) -> AttributeError:
        raise AttributeError(
            'net_amount is not a writeable attribute, use set_net_amount()  method to change its value.')

    @property
    def total_amount(self) -> int:
        if self.withheld_tax:
            return int(round(self.exent_amount + self.net_amount, 0))
        return int(round(self.exent_amount + self.net_amount + self.tax_amount, 0))

    @property
    def amount_to_be_paid(self) -> int:
        return self.total_amount + self.outstanding_balance

    def set_net_amount(self, amount: int, tax_inclusive: bool = False) -> int:

        if tax_inclusive:
            amount = int(round((amount / (self.tax_pct / 100 + 1)), 0))

        self.__net_amount = amount
        return self.__net_amount

    def lxml_element(self, voucher: bool = False) -> ET.Element:

        root = ET.Element('Totales')
        if self.net_amount:
            net_amount = ET.SubElement(root, 'MntNeto')
            net_amount.text = str(self.net_amount)

        if self.exent_amount:
            exent_amount = ET.SubElement(root, 'MntExe')
            exent_amount.text = str(self.exent_amount)

        if not voucher and self.net_amount:
            tax_pct = ET.SubElement(root, 'TasaIVA')
            tax_pct.text = str(round(self.tax_pct, 2))

        if self.net_amount:
            tax_amount = ET.SubElement(root, 'IVA')
            tax_amount.text = str(self.tax_amount)

        total_amount = ET.SubElement(root, 'MntTotal')
        total_amount.text = str(self.total_amount)

        if 0 != self.outstanding_balance is not None:
            outstanding_balance = ET.SubElement(root, 'SaldoAnterior')
            outstanding_balance.text = str(self.outstanding_balance)

        if 0 != self.amount_to_be_paid is not None:
            amount_to_be_paid = ET.SubElement(root, 'VlrPagar')
            amount_to_be_paid.text = str(self.amount_to_be_paid)

        return root

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'TotalsMixin':

        net_amount = element.find(prefix+'MntNeto')
        if net_amount is not None:
            net_amount = int(net_amount.text)

        exent_amount = element.find(prefix+'MntExe')
        if exent_amount is not None:
            exent_amount = int(exent_amount.text)

        outstanding_balance = element.find(prefix+'SaldoAnterior')
        if outstanding_balance is not None:
            outstanding_balance = int(outstanding_balance.text)

        amount_to_be_paid = element.find(prefix+'VlrPagar')
        if amount_to_be_paid is not None:
            amount_to_be_paid = int(amount_to_be_paid.text)

        return cls(net_amount, exent_amount, outstanding_balance=outstanding_balance or 0)
