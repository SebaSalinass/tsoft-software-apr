from email.policy import default
from sqlalchemy_utils import ArrowType
from sqlalchemy.ext.declarative import declared_attr

from app.domain.shared.constants import ActivableState
from ...domain.shared.mixins.activable import ActivableMixin
from ...db import db


class Activable(ActivableMixin):
    
    __abstract__ = True

    active_from = db.Column(ArrowType)
    active_from = db.Column(ArrowType)
    state = db.Column(db.Integer, default=ActivableState.INACTIVE)