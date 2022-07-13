from sqlalchemy_utils import UUIDType
from app.db import db


issuers_addresses = db.Table(
    'issuers_addresses',
    db.Column('issuer_id', UUIDType, db.ForeignKey('issuers.id'), unique=True),
    db.Column('address_id', UUIDType, db.ForeignKey('addresses.id'), unique=True)
)
