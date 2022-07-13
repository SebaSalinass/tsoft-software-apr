from uuid import uuid4

from arrow import Arrow, utcnow
from sqlalchemy_utils import UUIDType, ArrowType
from sqlalchemy.ext.mutable import MutableDict

from ...db import db
from ...domain.finance.mixins.charge import ChargeMixin
from ..secondaries.charge import (charges_services, charges_etds,
                                  charges_credit_notes, charges_transactions)
from ..shared.base import Model


__all__ = ('Charge',)


class Charge(Model, ChargeMixin):

    __tablename__ = 'charges'
    
    # ---------- Charge Mixin 
    user_id = db.Column(UUIDType, db.ForeignKey('users.id'))
    public_id = db.Column(db.String)
    amount = db.Column(db.Integer, nullable=False)
    paid_amount = db.Column(db.Integer, default=0)
    
    payload = db.Column(MutableDict.as_mutable(db.PickleType), nullable=False)
    expires_at = db.Column(ArrowType, default=utcnow)
    
    completed = db.Column(db.Boolean, default=False)
    nulled = db.Column(db.Boolean, default=False)
    renegotiated = db.Column(db.Boolean, default=False)
   
    service = db.relationship('Service', secondary=charges_services, uselist=False)
    transactions = db.relationship('Transaction', secondary=charges_transactions, 
                                   uselist=True, order_by='desc(Transaction.created_at)')
    etd = db.relationship('ETD', secondary=charges_etds, uselist=False)
    credit_note = db.relationship('ETD', secondary=charges_credit_notes, uselist=False)
    
    balance_id = db.Column(UUIDType, db.ForeignKey('balances.id'))
    
    @classmethod
    def new(cls, amount: int) -> 'Charge':
        new_id = uuid4()
        public_id = str(new_id.node)
        return cls(amount=amount, id=new_id, public_id=public_id)
        


