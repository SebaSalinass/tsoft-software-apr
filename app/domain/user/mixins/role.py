from ..constants import Permission


class RoleMixin:
    '''
    Class to identify permissions over user objects.
    '''

    name: str
    permissions: int = 0
    is_default: bool = False

    def add_permission(self, perm: Permission) -> None:
        '''
        Adds permissions if not granted before.
        '''
        if not self.has_permission(perm):
            self.permissions += perm.value

    def remove_permission(self, perm: Permission) -> None:
        '''
        Removes given permission if granted before.
        '''
        if self.has_permission(perm):
            self.permissions -= perm.value

    def reset_permissions(self) -> None:
        '''
        Resets permissions to 0
        '''
        self.permissions = 0

    def has_permission(self, perm: Permission) -> bool:
        '''
        Verifies if Role has given permission.
        Return `True/False`
        '''
        return self.permissions & perm.value == perm.value
