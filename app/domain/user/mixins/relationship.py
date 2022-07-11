from typing import Optional

#from ...finances.mixins.charge import ChargeMixin, PaymentPlanMixin
#from ...shared.mixins.address import AddressMixin


#class RelationshipMixin:
#    
#    address: Optional[AddressMixin] = None
#    charges: list[ChargeMixin] = None
#    payment_plans: list[PaymentPlanMixin] = None
#    
#    
#    def charges_pending(self) -> list[ChargeMixin]:
#        return [ charge for charge in self.charges if not charge.is_completed and not charge.nulled ]
#
#    def charges_completed(self) -> list[ChargeMixin]:
#        return [ charge for charge in self.charges if charge.is_completed ]
#
#    def total_debt(self) -> int:
#        return sum([charge.amount_to_be_paid() for charge in self.charges_pending()])
#
#    def current_debt(self) -> int:
#        return sum([charge.current_amount_to_be_paid() for charge in self.charges_pending()])

