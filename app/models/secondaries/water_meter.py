from sqlalchemy_utils import UUIDType
from app.db import db


water_meters_current_readings = db.Table(
    'water_meters_current_readings',
    db.Column('water_meter_id', UUIDType, db.ForeignKey('water_meters.id')),
    db.Column('reading_id', UUIDType, db.ForeignKey('readings.id'), unique=True)
)

water_meters_previous_readings = db.Table(
    'water_meters_previous_readings',
    db.Column('water_meter_id', UUIDType, db.ForeignKey('water_meters.id')),
    db.Column('reading_id', UUIDType, db.ForeignKey('readings.id'), unique=True)
)