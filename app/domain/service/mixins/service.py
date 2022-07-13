from typing import Any
from uuid import UUID

from arrow import utcnow

from ...shared.mixins.activable import ActivableMixin


class ServiceTypeMixin:
    
    code: str
    name: str
    description: str
    water_service: bool = False



class ServiceMixin(ActivableMixin):

    service_type: ServiceTypeMixin
    payload: dict[str, Any]
    