from sqlalchemy_utils import UUIDType
from app.db import db

charges_services = db.Table(
    'charge_services',
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True),
    db.Column('service_id', UUIDType, db.ForeignKey('services.id'))
)

charges_transactions = db.Table(
    'charges_transactions',
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id')),
    db.Column('transaction_id', UUIDType, db.ForeignKey('transactions.id'), unique=True)
)

charges_etds = db.Table(
    'charges_etds',
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True),
    db.Column('etd_id', UUIDType, db.ForeignKey('etds.id'), unique=True)
)

charges_credit_notes = db.Table(
    'charges_credit_notes',
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True),
    db.Column('etd_id', UUIDType, db.ForeignKey('etds.id'), unique=True)
)