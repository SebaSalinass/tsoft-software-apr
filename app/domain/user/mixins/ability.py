from .role import RoleMixin
from ..constants import Permission


class AbilityMixin:
    """Ability Mixin for users role behavior."""

    role: RoleMixin = None

    def can(self, perm: Permission) -> bool:
        """Shorthand for `user.role.has_permission(perm)`

        Args:
            perm (Permission): Permission to evaluate.

        Returns:
            bool: `True` if user.role has given permission.
        """
        return self.role.has_permission(perm)

    def is_administrator(self) -> bool:
        '''Checks if user has given Permission.ADMIN'''
        return self.can(Permission.ADMIN)