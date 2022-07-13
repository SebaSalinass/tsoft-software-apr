from arrow import Arrow
from sqlalchemy.orm import composite

from ...db import db
from ...domain.finance.mixins.balance import  BalanceMixin
from ..shared.base import Model


__all__ = ('Balance',)


class Balance(Model, BalanceMixin):

    __tablename__ = 'balances'
    
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    period = composite(Arrow, year, month)

    amount_base = db.Column(db.BigInteger)
    amount_expense = db.Column(db.BigInteger)
    amount_income = db.Column(db.BigInteger)
    amount_debt = db.Column(db.BigInteger)

    closed = db.Column(db.Boolean, default=False)

    # --------- SQLAlchemy relationships 
    charges = db.relationship('Charge', backref='balance', uselist=True)
    entries = db.relationship('Entry', backref='balance', uselist=True)
    expenses = db.relationship('Expense', backref='balance', uselist=True)
    transactions = db.relationship('Transaction', backref='balance', uselist=True)

    @classmethod
    def new(cls, month: int, year: int, amount_base: int, amount_expense: int,
            amount_income: int, amount_debt: int) -> 'Balance':
        
        return cls(month=month, year=year, amount_base=amount_base, 
                   amount_expense=amount_expense, amount_income=amount_income,
                   amount_debt=amount_debt)