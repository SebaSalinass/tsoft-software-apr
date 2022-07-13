from typing import Optional
from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.mutable import MutableDict

from ...db import db
from ...domain.finance.mixins.transaction import TransactionMixin
from ...domain.finance.constants import TransactionType
from ..shared.base import Model


__all__ = ('Transaction',)


class Transaction(Model, TransactionMixin):

    __tablename__ = 'transactions'
    # ---------- Transaction Mixin 
    amount = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False, default=TransactionType.CASH)
    payload = db.Column(MutableDict.as_mutable(db.JSON), default=dict)
    # ----------- SQLAlchemy relationships
    balance_id = db.Column(UUIDType, db.ForeignKey('balances.id'))
    
    @classmethod
    def new(cls, amount: int, type: TransactionType = TransactionType.CASH, 
            payload: Optional[dict[str,str]] = None) -> 'Transaction':
        
        return cls(amount=amount, type=type, payload=payload)