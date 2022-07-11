from typing import Optional
from arrow import Arrow, utcnow


class IdentitiyMixin():
    
    # --------- Required Values 
    rut: str
    name: str
    # ---------  User only further Information
    fst_sur: Optional[str] = None
    # ----------- Business only further Information    
    business_activity: Optional[str] = None
    # ----------- Optional further information 
    snd_sur: Optional[str] = None
    email: Optional[str] = None
    contact: Optional[str] = None
    # ----------- Optional information 
    last_seen: Optional[Arrow] = None
    is_active: bool = True
    is_business: bool = False
    is_partner: bool = False
    incorporation_date: Optional[Arrow] = None
    
    def ping(self) -> None:
        self.last_seen = utcnow()

    @property
    def fullname(self) -> str:
        if self.is_business:
            return self.name.title()
        return f'{self.name} {self.fst_sur or ""} {self.snd_sur or ""}'.rstrip().title()
    

