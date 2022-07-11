from dataclasses import dataclass, field


from .base import BaseMixin
from ...users.mixins.user import UserMixin


@dataclass
class ActionMixin(BaseMixin):
    
    owner: UserMixin # User Whos making the action
    receptor: UserMixin # User Whos making the action
    payload: dict[str, str] = field(default_factory=dict)

        
        
        
        
            
    
    
    
    