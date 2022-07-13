from sqlalchemy.ext.mutable import MutableDict

from ...db import db
from .base import Model
from ...domain.shared.mixins.action import ActionMixin
from ..secondaries.shared import actions_owner, actions_receptor


__all__ = ('Action',)


class Action(Model, ActionMixin):

    __tablename__ = 'actions'
    
    owner = db.relationship('User', secondary=actions_owner, uselist=False)
    receptor = db.relationship('User', secondary=actions_receptor, uselist=False)
    payload = db.Column(MutableDict.as_mutable(db.JSON), default=dict)