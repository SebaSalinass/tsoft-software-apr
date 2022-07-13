from typing import Iterator, Optional

from ...account.mixins.account import AccountMixin
from ...finance.mixins.charge import ChargeMixin
from ...finance.mixins.renegotiation import RenegotiationMixin
from ...shared.mixins.address import AddressMixin


class RelationshipMixin:
    
    address: Optional[AddressMixin] = None
    charges: list[ChargeMixin] = []
    renegotiations: list[RenegotiationMixin] = []
    
    incorporation_charge: Optional[ChargeMixin] = None
    accounts: list[AccountMixin]
    
    def pending_charges(self) -> Iterator[ChargeMixin]:
        yield from filter(lambda charge: charge.is_pending, self.charges)
        
    def pending_renegotiations(self) -> Iterator[RenegotiationMixin]:
        yield from filter(lambda renegotiation: renegotiation.is_pending, self.renegotiations)

    def debt(self) -> int:
        """Adds charges amount to be paid and renegotiation amount to be paid"""
        atbp_charges = sum([charge.debt() for charge in self.pending_charges()])
        atbp_renegotiations = sum([renegotiation.debt() for renegotiation in self.pending_renegotiations()])
        return atbp_charges + atbp_renegotiations

    def current_debt(self) -> int:
        """Adds charges amount to be paid and renegotiation current amount to be paid"""
        ob_charge = sum([charge.amount_to_be_paid() for charge in self.pending_charges()])
        ob_renegotiation = sum([renegotiation.current_debt() for renegotiation in self.pending_renegotiations()])
        return ob_charge + ob_renegotiation