from sqlalchemy_utils import UUIDType
from app.db import db

accounts_addresses = db.Table(
    'accounts_addresses',
    db.Column('account_id', UUIDType, db.ForeignKey('accounts.id'), unique=True),
    db.Column('address_id', UUIDType, db.ForeignKey('addresses.id'), unique=True)
)

accounts_current_water_meter = db.Table(
    'accounts_current_water_meter',
    db.Column('account_id', UUIDType, db.ForeignKey('accounts.id'), unique=True),
    db.Column('water_meter_id', UUIDType, db.ForeignKey('water_meters.id'), unique=True)
)

accounts_installation_charges = db.Table(
    'accounts_installation_charges',
    db.Column('account_id', UUIDType, db.ForeignKey('accounts.id'), unique=True),
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True)
)

accounts_charges = db.Table(
    'accounts_charges',
    db.Column('account_id', UUIDType, db.ForeignKey('accounts.id')),
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True)
)