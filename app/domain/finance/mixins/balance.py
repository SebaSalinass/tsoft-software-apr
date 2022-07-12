from typing import List
from arrow import Arrow, utcnow

from ...shared.mixins.base import BaseMixin
from .movements import EntryMixin, ExpenseMixin
from .transaction import TransactionMixin
from .charge import ChargeMixin

class BalanceMixin(BaseMixin):

    month: int
    year: int
    period: Arrow

    amount_base: int
    amount_expense: int
    amount_income: int
    amount_debt: int

    closed: bool = False

    charges: List[ChargeMixin] = []
    entries: list[EntryMixin] = []
    expenses: list[ExpenseMixin] = []
    transactions: list[TransactionMixin] = []

    def balance_total(self, include_on_debt: bool = False) -> int:
        """Calculates the balance total after adding incomes and substracting expenses.

        Args:
            include_on_debt (bool, optional): Includes the debt into the calculation. Defaults to False.

        Returns:
            int: The result amount
        """
        return self.amount_base + (self.amount_income - self.amount_expense) + \
            (self.amount_debt if include_on_debt else 0)

    @property
    def closeable(self) -> bool:
        if self.closed:
            return False
        return self.date_to.to('utc').date() <= utcnow().date()

    @property
    def date_from(self) -> Arrow:
        return self.period.floor('month')

    @property
    def date_to(self) -> Arrow:
        return self.period.ceil('month')
