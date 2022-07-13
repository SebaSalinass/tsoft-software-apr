from sqlalchemy_utils import UUIDType
from app.db import db


actions_owner = db.Table(
    'actions_owner',
    db.Column('action_id', UUIDType, db.ForeignKey('actions.id'), unique=True),
    db.Column('user_id', UUIDType, db.ForeignKey('users.id'))
)
actions_receptor = db.Table(
    'actions_receptor',
    db.Column('action_id', UUIDType, db.ForeignKey('actions.id'), unique=True),
    db.Column('user_id', UUIDType, db.ForeignKey('users.id'))
)
