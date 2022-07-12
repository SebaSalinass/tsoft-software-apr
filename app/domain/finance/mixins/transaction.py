from typing import Optional
from ...shared.mixins.base import BaseMixin
from ..constants import TransactionType


class TransactionMixin(BaseMixin):
    """Object that alocates basic transaction information
    """

    amount: int
    type: TransactionType = TransactionType.CASH
    payload: Optional[dict[str, str]] = None
