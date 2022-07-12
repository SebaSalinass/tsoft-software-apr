from typing import Optional, List
from uuid import UUID
from arrow import Arrow, utcnow

from ...shared.mixins.base import BaseMixin
from ..exceptions import ReadingInsertionError


class ReadingMixin(BaseMixin):

    value: int
    date: Arrow

    water_meter_id: Optional[UUID] = None

    def __add__(self, other: 'ReadingMixin') -> int:
        return self.value + other.value

    def __sub__(self, other: 'ReadingMixin') -> int:
        return self.value - other.value

    def __gt__(self, other: 'ReadingMixin') -> bool:
        return self.value > other.value

    def __lt__(self, other: 'ReadingMixin') -> bool:
        return self.value < other.value


class WaterMeterMixin:

    top_limit: int = 9999
    consumption: int = 0
    serial_number: Optional[str] = None
    current: bool = False

    current_reading: Optional[ReadingMixin] = None
    previous_reading: Optional[ReadingMixin] = None
    readings: List[ReadingMixin] = []

    account_id: Optional[UUID] = None

    @property
    def is_deletable(self):
        return not self.readings

    def needs_reading(self) -> bool:
        if self.current_reading:
            return self.current_reading.date.shift(months=1) <= utcnow().to('America/Santiago')
        return False

    def __reading_sanity_checks(self, reading: ReadingMixin) -> None:
        '''
            Performs checks of given Reading to validate it on its value and date insertion.
        '''
        # Verifying Measure Value is Valid -------------------------------------
        if not (0 <= reading.value <= self.top_limit):
            raise ReadingInsertionError('Valor de lectura invalido'
                f'''El valor de la lectura debe encontrarse entre 0 y 
                {self.top_limit!r}: valor ingresado {reading.value!r};''')

        if not self.current_reading:
            return

        # Verifying Measure Value is Valid -------------------------------------
        if self.current_reading > reading and \
            self.current_reading.value < self.top_limit - 300: #TODO Extraer esta variable
            raise ReadingInsertionError('Valor de lectura invalido',
                f'''El valor de la lectura debe ser mayor al de la ultima lectura ingresada; 
                valor lectura anterior: {self.current_reading.value!r}, 
                valor ingresado: {reading.value!r} ''')

        # Verifying Measure Date is Valid -------------------------------------
        if reading.date < self.current_reading.date.shift(months=1):
            raise ReadingInsertionError('Fecha de lectura invalido',
                f'''La fecha de lectura no puede ser menor a 1 mes desde la ultima ingresada: 
                {self.current_reading.date.format("DD/MM/YYYY")},
                valor ingresado:  {reading.date.format("DD/MM/YYYY")}.
                ''')

    def insert_reading(self, reading: ReadingMixin) -> None:
        '''
        Safely inserts measures if its has valid information.
        '''
        self.__reading_sanity_checks(reading)

        self.previous_reading = self.current_reading
        self.current_reading = reading
        self.readings.insert(0, reading)

        self.consumption += self.last_consumption()

    def remove_reading(self, reading: ReadingMixin) -> None:
        '''
            Safely removes measures ensuring the maintenance of a correct order.
        '''
        assert self.current_reading is reading

        last_consumption = self.last_consumption()
        self.readings.remove(reading)

        readings_len = len(self.readings)
        self.current_reading = self.readings[0] if readings_len > 0 else None
        self.previous_reading = self.readings[1] if readings_len > 1 else None

        self.consumption -= last_consumption

    def last_consumption(self) -> int:
        '''
        Return the last consumption from the last 2 readings or 0.
        '''
        if not self.previous_reading:
            return 0

        if self.current_reading < self.previous_reading:
            return self.top_limit - (self.previous_reading - self.current_reading)

        return self.current_reading - self.previous_reading
