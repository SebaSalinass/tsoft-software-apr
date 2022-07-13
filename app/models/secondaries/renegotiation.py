from sqlalchemy_utils import UUIDType
from app.db import db

renegotiation_transactions = db.Table(
    'renegotiation_transactions',
    db.Column('renegotiation_id', UUIDType, db.ForeignKey('renegotiations.id')),
    db.Column('transaction_id', UUIDType, db.ForeignKey('transactions.id'), unique=True)
)

renegotiation_charges = db.Table(
    'renegotiation_charges',
    db.Column('renegotiation_id', UUIDType, db.ForeignKey('renegotiations.id')),
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True)
)