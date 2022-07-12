from typing import Any

from arrow import utcnow

from ...shared.mixins.activable import ActivableMixin
from ...shared.constants import ActivableState


class ServiceTypeMixin:
    
    code: str
    name: str
    description: str
    is_water_service: bool = False



class ServiceMixin(ActivableMixin):

    service_type: ServiceTypeMixin
    payload: dict[str, Any]

    ## TODO SEND THIS TO MODEL CLASS
    @classmethod
    def new_water_service(cls, min_consumption: int, fst_leg_max: int, fixed_charge:int,
                          low_usage_surcharge:int, fst_leg_price: int, snd_leg_price: int,
                          service_type: ServiceTypeMixin) -> 'ServiceMixin':

        assert service_type.is_water_service

        payload = {
            'min_consumption': min_consumption,
            'fst_leg_max': fst_leg_max,
            'fixed_charge': fixed_charge,
            'low_usage_surcharge': low_usage_surcharge,
            'fst_leg_price': fst_leg_price,
            'snd_leg_price': snd_leg_price,
        }

        return cls(service_type=service_type, payload=payload)

    @classmethod
    def new_other_service(cls, price: int, service_type: ServiceTypeMixin) -> 'ServiceMixin':

        assert not service_type.is_water_service

        payload = {
            'price': price,            
        }

        return cls(service_type=service_type, payload=payload)
