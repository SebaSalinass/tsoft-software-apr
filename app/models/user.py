from uuid import UUID, uuid4
from typing import Optional, Union

from arrow import Arrow
from sqlalchemy_utils import UUIDType, ArrowType
from sqlalchemy.orm import validates

from ..db import db
from ..utils.validators import (validate_rut, validate_business_name, 
                              validate_user_name, valid_phone, validate_email)
from ..domain.user.mixins.user import UserMixin
from ..domain.user.mixins.role import RoleMixin
from ..domain.user.constants import Permission
from .shared.base import Model
from .secondaries.user import users_roles, users_incorporation_charges


__all__ = ('User', 'Role',)


class Role(Model, RoleMixin):
    '''
    Role Model united with Mixin model for all object implementations
    '''
    __tablename__ = 'roles'
    # Role Mixin ---------------------------------------------------------
    name = db.Column(db.String(30), nullable=False, unique=True)
    permissions = db.Column(db.Integer, default=0)
    default = db.Column(db.Boolean, default=False)

    @classmethod
    def new(cls, name: str, permissions: int = 0, default: bool = False) -> 'Role':
        return cls(name=name, permissions=permissions, default=default)

    @classmethod
    def default_role(cls) -> 'Role':
        return cls.first(default=True)
    
    @classmethod
    def insert_test_roles(cls) -> None:
        '''
        Adds testing roles to db session.
        Must be commited 
        '''

        roles = {
            'user': [
                Permission.READ
            ],
            'administrative': [
                Permission.READ,
                Permission.MANAGE_USERS,
                Permission.MANAGE_INVENTORY
            ],
            'treasurer': [
                Permission.READ,
                Permission.MANAGE_SERVICE,
                Permission.MANAGE_ACCOUNTS,
                Permission.MANAGE_USERS
            ],
            'admin': [
                Permission.READ,
                Permission.MANAGE_ACCOUNTS,
                Permission.MANAGE_SERVICE,
                Permission.MANAGE_USERS,
                Permission.MANAGE_INVENTORY,
                Permission.ADMIN
            ]
        }
    
        default_role = 'user'

        for role_name, role_perms in roles.items():
                role = Role(role_name)
                for perm in role_perms:
                    role.add_permission(perm)
                role.default = (role.name == default_role)
                db.session.add(role)
        
        return
    

class User(Model, UserMixin):
    '''
    User Model united with Mixin model for all object implementations
    '''
    __tablename__ = 'users'

    id = db.Column(UUIDType, primary_key=True, default=uuid4)
    # ---------- Identity Mixin 
    rut = db.Column(db.String(10), nullable=False, index=True, unique=True)
    name = db.Column(db.String(80), nullable=False)
    # ---------- User only further Information
    fst_sur = db.Column(db.String(50))
    # ----------- Business only further Information
    business_activity = db.Column(db.String(80))
    # ----------- Optional information 
    snd_sur = db.Column(db.String(50))
    email = db.Column(db.String(125))
    contact = db.Column(db.String(12))
    # ----------- Optional Platform information 
    last_seen = db.Column(ArrowType)
    active = db.Column(db.Boolean, default=True)
    incorporation_date = db.Column(ArrowType)
    # ----------- Auth Mixin
    password_hash = db.Column(db.LargeBinary(128), nullable=False)
    # ----------- Ability Mixin
    role = db.relationship('Role', secondary=users_roles, uselist=False)
    # -----------SQLAlchemy relationships
    address = db.relationship('Address', uselist=False)
    charges = db.relationship('Charge', backref='user')
    renegotiations = db.relationship('PaymentPlan', backref='user', uselist=True)
    
    incorporation_charge = db.relationship('Charge', secondary=users_incorporation_charges, uselist=False)
    accounts = db.relationship('Account', backref='user', uselist=True, order_by='Account.created_at')

    @validates('rut', 'name', 'fst_sur', 'snd_sur', 'email', 'contact', 'is_business')
    def validate_data(self, key: str, value: str) -> Union[str, None, bool]:
        if key == 'rut':
            assert validate_rut(value)
            return value.upper().replace('.', '')

        elif key in ('fst_sur', 'snd_sur'):
            if not value:
                return None
            assert validate_user_name(value)
            return value.lower()
        
        elif key == 'name':
            assert value is not None and (validate_user_name(value) or validate_business_name(value))
            return value.lower()

        elif key == 'email':
            if not value:
                return None
            assert validate_email(value)
            return value.lower()

        elif key == 'contact':
            if not value:
                return None
            assert valid_phone(value)
            return value.lower()


    @classmethod
    def new(cls, rut: str, name: str, fst_sur: Optional[str] = None, business_activity: Optional[str] = None,
            snd_sur: Optional[str] = None, email: Optional[str] = None, contact: Optional[str] = None, 
            incorporation_date: Optional[Arrow] = None, role: Optional[Role] = None, **kwargs) -> 'User':
        
        assert (fst_sur and not business_activity) or (business_activity and not fst_sur)
        password = kwargs.get('password', rut[0:6])
        role = role or Role.default_role()
        
        return cls(rut=rut, name=name, fst_sur=fst_sur, business_activity=business_activity, snd_sur=snd_sur,
                   password=password, email=email, contact=contact, incorporation_date=incorporation_date,
                   role=role)


    @classmethod
    def insert_test_users(cls) -> None:
        '''
        Adds testing users to db session.
        Must be commited 
        '''        
        
        users_list = [
            {
                'rut': '8743174-6',
                'name': 'User',
                'fst_sur': 'Admin',
                'role': Role.first(name='admin')
            },
            {
                'rut': '11143692-4',
                'name': 'User',
                'fst_sur': 'Administrative',
                'role': Role.first(name='administrative')
            },
            {
                'rut': '11409033-6',
                'name': 'User',
                'fst_sur': 'Treasurer',
                'role': Role.first(name='treasurer')
            },
            {
                'rut': '14269074-8',
                'name': 'User',
                'fst_sur': 'Default',
            },
        ]
        
        business_list = [
            {
                'rut': '36727901-K',
                'name': 'User Business Test',
                'business_activity': 'Business Activity Test',
                'address': {'address':'Test Address 1', 'city':'City', 'commune':'Commune'}
            }
        ]

        for obj_dict in users_list:            
            user = User.new_regular_user(**obj_dict)
            db.session.add(user)
            
        for obj_dict in business_list:            
            user = User.new_business_user(**obj_dict)
            db.session.add(user)
            
        return


def user_loader(id: str) -> User:
    return User.get(UUID(id))
