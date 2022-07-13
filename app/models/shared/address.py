import re

from sqlalchemy.orm import validates
from sqlalchemy_utils import UUIDType

from ...db import db
from ...domain.shared.mixins.address import AddressMixin
from .base import Model


__all__ = ('Address',)


class Address(Model, AddressMixin):

    __tablename__ = 'addresses'

    city = db.Column(db.String(20))
    commune = db.Column(db.String(20))
    address = db.Column(db.String(80))
    postal_code = db.Column(db.Integer)
    
    user_id = db.Column(UUIDType, db.ForeignKey('users.id'))
    service_account_id = db.Column(UUIDType, db.ForeignKey('service_accounts.id'))
    
    def __init__(self, address: str, city: str = None, commune: str = None, **kwargs) -> None:
        super(Address, self).__init__(**kwargs)
        self.address = address
        self.city = city
        self.commune = commune


    @validates('city', 'commune', 'address')
    def validate_attrs(self, key: str, value: str) -> str:

        if key == 'city' or key == 'commune':
            if not value: 
                return
            assert re.match(r'^(?![\s.]+$)[a-zA-Z\s.#]{3,20}$', value)
            return value.strip().lower()

        if key == 'address':
            assert re.match(r'^(?![\s.]+$)[a-zA-Z0-9\s.#,/]{3,80}$', value)
            return value.strip()
