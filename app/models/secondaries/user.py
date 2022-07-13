from sqlalchemy_utils import UUIDType
from app.db import db

users_roles = db.Table(
    'users_roles',
    db.Column('user_id', UUIDType, db.ForeignKey('users.id'), unique=True),
    db.Column('role_id', UUIDType, db.ForeignKey('roles.id'))
)

users_addresses = db.Table(
    'users_addresses',
    db.Column('user_id', UUIDType, db.ForeignKey('users.id'), unique=True),
    db.Column('address_id', UUIDType, db.ForeignKey('addresses.id'), unique=True)
)

users_incorporation_charges = db.Table(
    'users_incorporation_charges',
    db.Column('user_id', UUIDType, db.ForeignKey('users.id'), unique=True),
    db.Column('charge_id', UUIDType, db.ForeignKey('charges.id'), unique=True)
)
