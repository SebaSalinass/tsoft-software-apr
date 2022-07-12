from typing import Optional
from arrow import Arrow, utcnow

from ..constants import ActivableState


class ActivableMixin:
    '''
    BaseMixin class for other objects adding `id`, `created_at`,`updated_at` attributes
    and their respectives default values if not given
    '''
    active_from: Optional[Arrow] = None
    active_to: Optional[Arrow] = None
    state: ActivableState = ActivableState.INACTIVE

    def activate(self) -> None:
        """Sets internal state to `ACTIVE` and sets `active_from` attr to utcnow().
        """
        self.active_from = utcnow()
        self.state = ActivableState.ACTIVE


    def deactivate(self) -> None:
        """Sets internal state to `INACTIVE` and sets `active_to` attr to utcnow().
        """
        self.active_to = utcnow()
        self.state = ActivableState.INACTIVE
