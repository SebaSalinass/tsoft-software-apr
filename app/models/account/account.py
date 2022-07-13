from typing import Optional

from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.mutable import MutableDict

from ...db import db
from ...domain.account.mixins.account import AccountMixin
from ...domain.account.constants import SubsidyType
from ..secondaries.account import (accounts_addresses, accounts_current_water_meter, 
                                   accounts_installation_charges, accounts_charges)
from ..shared.base import Model


__all__ = ('Account',)


class Account(Model, AccountMixin):

    __tablename__ = 'accounts'
    # --------- AccountMixin information
    user_id = db.Column(UUIDType, db.ForeignKey('users.id'))
    public_id = db.Column(db.String(20))
    address = db.relationship('Address', secondary=accounts_addresses, uselist=False)
    
    is_active = db.Column(db.Boolean, default=True)
    is_water_cut = db.Column(db.Boolean, default=False)
    last_13 = db.Column(MutableDict.as_mutable(db.PickleType), default=dict)
    
    subsidy_type = db.Column(db.Integer, default=SubsidyType.NONE)
    subsidy_amount = db.Column(db.Integer)
    fst_leg_exent = db.Column(db.Boolean, default=False)
    fixed_charge_exent = db.Column(db.Boolean, default=False)
    exempt_from_payment = db.Column(db.Boolean, default=False)
    paid_installation = db.Column(db.Boolean, default=False)
    
    installation_charge = db.relationship('Charge', secondary=accounts_installation_charges, uselist=False)
    current_water_meter = db.relationship('WaterMeter', secondary=accounts_current_water_meter, uselist=False, lazy='joined')
    water_meters = db.relationship('WaterMeter', backref='account', order_by='desc(WaterMeter.created_at)', uselist=True)
    charges = db.relationship('Charge', secondary=accounts_charges, uselist=True, order_by='desc(Charge.created_at)', lazy='joined')
    renegotiations = db.relationship('Renegotiation', backref='account', uselist=True, lazy='joined')


    @classmethod
    def new(cls, public_id: str, subsidy_type: Optional[SubsidyType] = None,
            subsidy_amount: Optional[int] = None, fixed_charge_exent: bool = False, exempt_from_payment: bool = False,
            fst_leg_exent: bool = False, paid_installation: bool = False) -> 'Account':

        return cls(public_id=public_id, subsidy_type=subsidy_type, subsidy_amount=subsidy_amount, fst_leg_exent=fst_leg_exent,
                   fixed_charge_exent=fixed_charge_exent,exempt_from_payment=exempt_from_payment,paid_installation=paid_installation)
        
    @classmethod
    def new_public_id(cls, prefix: str, lenght: int) -> str:

        last_serviceaccount = cls.last_added()
        last_added_int = 0

        if last_serviceaccount:

            last_added_int = int(
                last_serviceaccount.public_id.split(prefix)[1])

        return prefix + str(last_added_int + 1).rjust(lenght, '0')
