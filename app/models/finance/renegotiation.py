from uuid import uuid4
from arrow import Arrow
from sqlalchemy_utils import ArrowType, UUIDType

from ...db import db
from ...domain.finance.mixins.renegotiation import RenegotiationMixin, InstallmentMixin
from ..shared.base import Model
from ..secondaries.renegotiation import renegotiation_charges, renegotiation_transactions


__all__ = ('Installment', 'Renegotiation',)


class Installment(Model, InstallmentMixin):

    __tablename__ = 'installments'
    # ---------- InstallmentMixin
    amount = db.Column(db.Integer, nullable=False)
    expires_at = db.Column(ArrowType)
    paid_amount = db.Column(db.Integer, nullable=False, default=0)
    completed = db.Column(db.Boolean, default=False)
    
    # -------- SQLAlchemy relationships
    renegotiation_id = db.Column(db.ForeignKey('renegotiations.id'))
    
    @classmethod
    def new(cls, amount: int, expires_at: Arrow) -> 'Installment':        
        return cls(amount=amount, expires_at=expires_at)
        

class Renegotiation(Model, RenegotiationMixin):

    __tablename__ = 'renegotiations'

    user_id = db.Column(UUIDType, db.ForeignKey('users.id'))
    public_id = db.Column(db.String(), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    paid_amount = db.Column(db.Integer, nullable=False, default=0)
    
    completed = db.Column(db.Boolean, default=False)
    charges = db.relationship('Charge', backref='renegotiation', 
                              secondary=renegotiation_charges, uselist=True)
    

    installments = db.relationship('Installment', order_by='Installment.expires_at', uselist=True)
    transactions = db.relationship('Transaction', secondary=renegotiation_transactions, 
                                   uselist=True, order_by='desc(Transaction.created_at)')
    
    @classmethod
    def new(cls, amount: int) -> 'Renegotiation':
        new_id = uuid4()
        public_id = str(new_id.node)
        return cls(amount=amount, id=new_id, public_id=public_id)
