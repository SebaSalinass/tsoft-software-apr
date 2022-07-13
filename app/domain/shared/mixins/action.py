from .base import BaseMixin
from ...user.mixins.user import UserMixin


class ActionMixin(BaseMixin):
    
    owner: UserMixin # User Whos making the action
    receptor: UserMixin # User Whos making the action
    payload: dict[str, str]

        
        
        
        
            
    
    
    
    