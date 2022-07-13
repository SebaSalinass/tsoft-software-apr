from typing import Optional
from arrow import utcnow, Arrow
from sqlalchemy_utils import ArrowType, UUIDType

from ...db import db
from ...domain.account.mixins.water_meter import WaterMeterMixin, ReadingMixin
from ..secondaries.water_meter import water_meters_current_readings, water_meters_previous_readings
from ..shared.base import Model
from ..shared.activable import Activable


__all__ = ('Reading', 'WaterMeter',)


class Reading(Model, ReadingMixin):

    __tablename__ = 'readings'

    value = db.Column(db.Integer, nullable=False)
    date = db.Column(ArrowType, nullable=False, default=utcnow)

    # relationships
    water_meter_id = db.Column(UUIDType, db.ForeignKey('water_meters.id'))
    
    @classmethod
    def new(cls, value: int, date: Optional[Arrow] = None) -> 'Reading':
        """Creates a new Reading instance

        Args:
            value (int): The Reading value
            date (Optional[Arrow], optional): The Reading date if `None` then current utc 
                                              is setted. Defaults to `None`.

        Returns:
            Reading: _description_
        """
        return cls(value=value, date=date or utcnow())


class WaterMeter(Model, Activable, WaterMeterMixin):

    __tablename__ = 'water_meters'
    
    serial_number = db.Column(db.String(30))
    top_limit = db.Column(db.Integer, nullable=False, default=9999)
    consumption = db.Column(db.Integer, default=0)

    current_reading = db.relationship('Reading', secondary=water_meters_current_readings, 
                                      uselist=False)
    previous_reading = db.relationship('Reading', secondary=water_meters_previous_readings, 
                                       uselist=False)
    readings = db.relationship('Reading', backref='water_meter', order_by='desc(Reading.date)', 
                               uselist=True, lazy='joined')

    # Platform Needs ----------------------------------------------------------
    account_id = db.Column(UUIDType, db.ForeignKey('accounts.id'))
        
    @classmethod
    def new(cls, serial_number: str = None, top_limit: int = 9999) -> 'WaterMeter':
        return cls(serial_number=serial_number, top_limit=top_limit)
