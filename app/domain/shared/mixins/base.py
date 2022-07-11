from typing import Optional
from uuid import UUID

from arrow import Arrow


class BaseMixin:
    '''
    BaseMixin class for other objects adding `id`, `created_at`,`updated_at` attributes
    and their respectives default values if not given
    '''
    id: Optional[UUID]
    created_at: Optional[Arrow]
    updated_at: Optional[Arrow]



