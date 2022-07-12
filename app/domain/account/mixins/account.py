from typing import Optional, Iterator
from uuid import UUID

from arrow import Arrow

from ...shared.mixins.base import BaseMixin
from ...shared.mixins.address import AddressMixin
from ...finance.mixins.charge import ChargeMixin
from ...finance.mixins.renegotiation import RenegotiationMixin
from ...service.mixins.service import ServiceTypeMixin

from ..constants import SubsidyType, AccountState
from .water_meter import WaterMeterMixin


class AccountMixin(BaseMixin):

    user_id: UUID
    public_id: str
    address: AddressMixin

    is_active: bool = True
    is_water_cut: bool = False
    last_13: Optional[dict[str, int]] = {}

    # Discount Properties -----------------------------------------------------
    subsidy_type: Optional[SubsidyType] = None
    subsidy_amount: Optional[int] = None
    fst_leg_exent: bool = False
    fixed_charge_exent: bool = False
    exempt_from_payment: bool = False
    paid_installation: bool = False

    # Installation Information ------------------------------------------------
    installation_charge: Optional[ChargeMixin] = []
    current_water_meter: Optional[WaterMeterMixin] = []
    water_meters: list[WaterMeterMixin] = []
    charges: list[ChargeMixin] = []
    renegotiations: list[RenegotiationMixin] = []

    @property
    def state(self):
        if not self.is_active:
            return AccountState.DISABLED
        if self.is_water_cut:
            return AccountState.WATER_CUT
        for charge in self.pending_charges():
            if charge.has_expired_over(months=1):
                return AccountState.CUT_IN_PROCESS
        return AccountState.ACTIVE

    @property
    def is_deletable(self) -> bool:

        if self.current_water_meter and not self.current_water_meter.is_deletable:
            return False
        if self.charges:
            return False
        return True

    def last_consumption(self)-> int:
        """Shortcut for `self.current_water_meter.last_consumption()` """
        return self.current_water_meter.last_consumption()
    
    def pending_charges(self) -> Iterator[ChargeMixin]:
        yield from filter(lambda charge: not charge.completed and not charge.renegotiated, self.charges)
    
    def pending_renegotiations(self) -> Iterator[RenegotiationMixin]:
        yield from filter(lambda renegotiation: not renegotiation.completed, self.renegotiations)

    def insert_watermeter(self, water_meter: WaterMeterMixin) -> None:
        """Safely inserts a new watermeter an sets it ass the current one for this account"""
        if self.current_water_meter:
            self.current_water_meter.current = False
        
        water_meter.current = True
        self.current_water_meter = water_meter
        self.water_meters.append(water_meter)
        return

    def total_consumption(self) -> int:
        """The total amount of water consumption for this account"""
        return sum([water_meter.consumption for water_meter in self.water_meters])

    def outstanding_balance(self) -> int:
        """Adds charges amount to be paid and renegotiation current amount to be paid"""
        ob_charge = sum([charge.amount_to_be_paid() for charge in self.pending_charges()])
        ob_renegotiation = sum([renegotiation.current_amount_to_be_paid() for renegotiation in self.pending_renegotiations()])
        return ob_charge + ob_renegotiation

    def amount_to_be_paid(self) -> int:
        """Adds charges amount to be paid and renegotiation amount to be paid"""
        atbp_charges = sum([charge.amount_to_be_paid() for charge in self.pending_charges()])
        atbp_renegotiations = sum([renegotiation.amount_to_be_paid() \
                                    for renegotiation in self.pending_renegotiations()])
        return atbp_charges + atbp_renegotiations

    def update_last_13(self, month: Arrow, consumption: int ) -> None:
        """Safely inserts month and consumption to last_13 set.

        Args:
            month (Arrow): Consumption month
            consumption (int): Consumption amount
        """
        if len(self.last_13) == 13:
            self.last_13.pop(next(iter(self.last_13)))

        self.last_13[month] = consumption

        return

    def get_water_charges(self) -> Iterator[ChargeMixin]:
        """Returns only water_service charges if any"""
        yield from filter(lambda charge: charge.service.service_type.is_water_service and \
                          not charge.nulled, self.charges)

    def water_charge_available(self) -> bool:
        '''Checks if the account needs a water Charge'''
        if not self.current_water_meter:
            return False

        if len(self.current_water_meter.readings) < 2:
            return False

        if self.current_water_meter.last_consumption() == 0 and self.fixed_charge_exent:
            return False

        if not self.charges:
            return True

        for charge in self.get_water_charges():
            if self.current_water_meter.current_reading.id == UUID(charge.payload['current_reading_id']):
                return False

        return True

    def installation_charge_available(self) -> bool:

        if self.paid_installation or self.installation_charge:
            return False
        return True

    def last_reading_updateable(self) -> bool:
        '''Checks if the last reading can be updated or edited.'''
        if not self.current_water_meter or not self.current_water_meter.current_reading:
            return False

        if not self.charges:
            return True

        for charge in self.get_water_charges():
            if charge.payload['current_reading_id'] == \
               str(self.current_water_meter.current_reading.id):
                return False

        return True

    def last_charge_of_service_type(self, service_type: ServiceTypeMixin) -> Optional[ChargeMixin]:
        '''Returns the last inserted Charge for the given service_type object'''
        for charge in self.charges:
            if charge.service.service_type == service_type:
                return charge

        return None
