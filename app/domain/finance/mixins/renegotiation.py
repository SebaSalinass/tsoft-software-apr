from typing import List, Iterator
from uuid import UUID

from arrow import Arrow, utcnow

from .charge import ChargeMixin
from .transaction import TransactionMixin
from ...shared.mixins.base import BaseMixin
from ..constants import InstallmentState, RenegotiationState

class InstallmentMixin(BaseMixin):

    amount: int
    paid_amount: int = 0
    expires_at: Arrow

    completed: bool = False

    @property
    def is_deletable(self) -> bool:
        return self.amount_to_be_paid() == self.amount

    @property
    def state(self) -> InstallmentState:
        if self.completed:
            return InstallmentState.COMPLETED

        if self.expires_at.date() < utcnow().to('America/Santiago').date():
            return InstallmentState.EXPIRED

        return InstallmentState.PENDING

    def amount_to_be_paid(self) -> int:
        '''
        Shortcut for `self.amount - self.paid_amount`
        '''
        return self.amount - self.paid_amount

    def days_to_expiration(self) -> int:
        """Returns the amount of days left for this payment to be expired

        Returns:
            int: Days
        """
        return (self.expires_at.date() - utcnow().date()).days


class RenegotiationMixin(BaseMixin):

    user_id: UUID
    public_id: str
    amount: int
    paid_amount: int = 0

    completed: bool = False
    charges: List[ChargeMixin] = []
    installments: List[InstallmentMixin] = []
    transactions: list[TransactionMixin] = []

    @property
    def state(self) -> RenegotiationState:
        if self.completed:
            return RenegotiationState.COMPLETED
 
        for installment in self.installments_left():
            installment_state = installment.state
            days_to_expiration = installment.days_to_expiration()
            
            if installment_state == InstallmentState.EXPIRED:
                return RenegotiationState.OVERDUE
            
            if installment_state == InstallmentState.PENDING and days_to_expiration > 5:
                return RenegotiationState.UP_TO_DATE
            
            if installment_state == InstallmentState.PENDING and days_to_expiration <= 5:
                return RenegotiationState.PENDING

    def installments_left(self) -> Iterator[InstallmentMixin]:
        """Returns all of the not completed installments in this renegotiation.

        Yields:
            Iterator[InstallmentMixin]: Installment not completed
        """
        yield from filter(lambda installment: not installment.completed, self.installments)

    def expired_installments(self) -> Iterator[InstallmentMixin]:
        """Returns all of the expired installments in this renegotiation.

        Yields:
            Iterator[InstallmentMixin]: Installment expired
        """
        yield from filter(lambda installment: installment.expires_at <= utcnow().to('America/Santiago'), self.installments_left())

    def amount_to_be_paid(self) -> int:
        """Shortcut for `self.amount - self.paid_amount`
        """
        return self.amount - self.paid_amount

    def current_amount_to_be_paid(self) -> int:        
        return sum([installment.amount_to_be_paid() for installment in self.expired_installments()])

    def has_expired_over(self, months: int = 1, days: int = 0) -> bool:
        """Verifies if the current Charge object has expired over the given time

        Args:
            months (int, optional): Months. Defaults to 1.
            days (int, optional): Days. Defaults to 0.

        Returns:
            bool: True if the expire_at date has passed over the given time
        """
        if self.completed:
            return False

        expires_at = next(self.installments_left())[0].expires_at

        return expires_at.shift(months=months, days=days) < utcnow()

    def accept_transaction(self, transaction: TransactionMixin) -> None:
        """Safely inserts the given transaction into the objects transaction list
        updating inner states and attributes.

        Args:
            transaction (TransactionMixin): The Transaction object

        Raises:
            ValueError: When transaction exceeds the amount to be paid or already completed.
        """
        if self.completed or not (0 < transaction.amount <= self.amount_to_be_paid()):
            raise ValueError('Transaction object invalid amount or charge already completed')
        
        transaction_amount = transaction.amount
        
        for installment in self.installments_left():
            if 0 < transaction_amount < installment.amount_to_be_paid():
                installment.paid_amount += transaction_amount

            elif transaction_amount >= installment.amount_to_be_paid():
                transaction_amount -= installment.amount_to_be_paid()
                installment.paid_amount = installment.amount
                installment.completed = True
        
        self.transactions.append(transaction)
        self.completed = (self.amount_to_be_paid() == 0)
    
"""
    @classmethod
    def construct_from_charges(cls, charges: list[ChargeMixin],  payment_cls: Callable[..., PaymentMixin],
                               installments: int, start_exp_date: Arrow = None) -> 'PaymentPlanMixin':
        assert installments > 1
        
        start_exp_date = start_exp_date.to('utc') if start_exp_date else utcnow()
        total_amount = sum([charge.amount for charge in charges])
        paid_amount = sum([charge.paid_amount for charge in charges])

        # Calculate installments ----------------------------------------------
        quota_total = total_amount - paid_amount
        quota_amount = int(round(quota_total / installments, 0))
        quota_rest = quota_amount % 10

        payments = []
        if quota_rest:
            quota_amount -= quota_rest

        for i in range(installments):
            if i == installments - 1:
                quota_amount = quota_total - (quota_amount * (installments - 1)) 
            
            payment = payment_cls(amount=quota_amount, expires_at=start_exp_date.shift(months=i))
            payments.append(payment)
        
        
        for charge in charges:
            charge.in_payment_plan = True

        return cls(amount=quota_total, charges=charges, payments=payments)
"""
