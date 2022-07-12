from typing import Optional
from uuid import UUID
from arrow import Arrow

from ...shared.mixins.base import BaseMixin
from ..constants import TransactionType

class ExpenseMixin(BaseMixin):
    """Basic expense mixin"""

    amount: int
    receptor: str
    date_emited: Arrow
    transaction_type: TransactionType = TransactionType.CASH

    folio: Optional[int] = None
    description: Optional[str] = None
    balance_id: Optional[UUID] = None


    @property
    def is_updateable(self) -> bool:
        if self.balance_id:
            return False
        return True



class EntryMixin(BaseMixin):
    """Basic entry mixin"""
    
    amount: int
    issuer: str    
    date_received: Arrow
    transaction_type: TransactionType = TransactionType.CASH

    folio: Optional[int] = None
    description: Optional[str] = None    
    balance_id: Optional[UUID] = None

    @property
    def is_updateable(self) -> bool:
        if self.balance_id:
            return False
        return True
