from typing import Optional
from arrow import Arrow, utcnow
from sqlalchemy_utils import ArrowType, UUIDType

from ...db import db
from ..shared.base import Model
from ...domain.finance.mixins.extras import ExpenseMixin, EntryMixin
from ...domain.finance.constants import TransactionType


__all__ = ('Expense', 'Entry',)


class Expense(Model, ExpenseMixin):

    __tablename__ = 'expenses'

    amount = db.Column(db.Integer)
    receptor = db.Column(db.String(80), nullable=False)
    date_emited = db.Column(ArrowType, default=utcnow)
    transaction_type = db.Column(db.Integer, default=TransactionType.CASH)
    
    folio = db.Column(db.BigInteger)
    description = db.Column(db.String(200))
    balance_id = db.Column(UUIDType, db.ForeignKey('balances.id'))
    
    @classmethod
    def new(cls, amount: int, receptor: str, date_emited: Optional[Arrow] = None, 
            transaction_type: TransactionType = TransactionType.CASH, **kwargs) -> 'Expense':

        return cls(amount=amount, receptor=receptor, date_emited=date_emited, 
                   transaction_type=transaction_type, **kwargs)


class Entry(Model, EntryMixin):

    __tablename__ = 'entries'

    amount = db.Column(db.Integer)
    issuer = db.Column(db.String(80))
    date_received = db.Column(ArrowType, default=utcnow)

    transaction_type = db.Column(db.Integer, default=TransactionType.CASH)
    folio = db.Column(db.BigInteger)
    description = db.Column(db.String(200))

    # --------- SQLAlchemy relationships
    balance_id = db.Column(UUIDType, db.ForeignKey('balances.id'))
    
    @classmethod
    def new(cls, amount: int, issuer: str, date_received: Optional[Arrow] = None, 
            transaction_type: TransactionType = TransactionType.CASH, **kwargs) -> 'Entry':

        return cls(amount=amount, issuer=issuer, date_received=date_received, 
                   transaction_type=transaction_type, **kwargs)