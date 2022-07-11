from .ability import AbilityMixin
from .identity import IdentitiyMixin
from .auth import AuthMixin
from ...shared.mixins.base import BaseMixin

class UserMixin(AuthMixin, AbilityMixin, IdentitiyMixin, BaseMixin):
    """Mixin Class for user behavior"""
