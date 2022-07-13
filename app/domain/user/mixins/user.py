from .ability import AbilityMixin
from .identity import IdentitiyMixin
from .auth import AuthMixin
from .relationship import RelationshipMixin
from ...shared.mixins.base import BaseMixin

class UserMixin(IdentitiyMixin, AuthMixin, AbilityMixin, RelationshipMixin, BaseMixin):
    """Mixin Class for user behavior"""
