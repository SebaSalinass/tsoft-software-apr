from typing import Optional, List, Any
from uuid import UUID

from arrow import Arrow, utcnow

from ...service.mixins.service import ServiceMixin

from .transaction import TransactionMixin
from ..constants import ChargeState
from ...shared.mixins.base import BaseMixin
from ...etd.mixins.etd import ETDMixin



class ChargeMixin(BaseMixin):

    user_id: UUID
    public_id: str
    amount: int
    paid_amount: int = 0

    payload: dict[str, Any]
    expires_at: Optional[Arrow] = None

    completed: bool = False
    nulled: bool = False
    renegotiated: bool = False

    service: Optional[ServiceMixin] = None
    transactions: List[TransactionMixin] = []
    etd: Optional[ETDMixin] = None
    credit_note: Optional[ETDMixin] = None

    balance_id: Optional[UUID] = None

    @property
    def etd_sent(self) -> bool:
        return self.etd.sii_sent

    @property
    def is_deletable(self) -> bool:
        return self.amount_to_be_paid() == self.amount and not self.etd_sent and not self.renegotiated

    @property
    def is_nullable(self) -> bool:
        return not self.is_deletable and self.paid_amount == 0

    @property
    def is_pending(self) -> bool:
        return not self.completed and not self.renegotiated and not self.nulled

    @property
    def state(self) -> ChargeState:
        if self.completed:
            return ChargeState.COMPLETED
        
        if self.is_nulled:
            return ChargeState.NULLED

        if self.renegotiated:
            return ChargeState.RENEGOTIATED
        
        if self.expires_at.date() < utcnow().to('America/Santiago').date():
            return ChargeState.OVERDUE
        
        return ChargeState.PENDING

    def debt(self) -> int:
        """Shortcut for `self.amount - self.paid_amount`
        """
        return self.amount - self.paid_amount

    def accept_transaction(self, transaction: TransactionMixin) -> None:
        """Safely inserts the given transaction into the objects transaction list
        updating inner states and attributes.

        Args:
            transaction (TransactionMixin): The Transaction object

        Raises:
            ValueError: When transaction exceeds the amount to be paid.
        """

        if self.completed or not (0 < transaction.amount <= self.amount_to_be_paid()):
            raise ValueError('Transaction object invalid amount or charge already completed')

        self.paid_amount += transaction.amount
        self.transactions.append(transaction)
        self.completed = (self.amount_to_be_paid() == 0)

    def days_to_expiration(self) -> int:
        """Returns the amount of days left for this charge to be expired.
        """
        return (self.expires_at - utcnow()).days

    def has_expired_over(self, months:int = 0, days: int = 0) -> bool:
        """Verifies if the current Charge object has expired over the given time

        Args:
            months (int, optional): Months. Defaults to 0.
            days (int, optional): Days. Defaults to 0.

        Returns:
            bool: True if the expire_at date has passed over the given time
        """
        if self.completed or not self.expires_at:
            return False

        return self.expires_at.shift(months=months, days=days) < utcnow()

      

