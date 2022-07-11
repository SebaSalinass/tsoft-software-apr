from dataclasses import dataclass
from typing import Optional

from .base import BaseMixin


@dataclass
class AddressMixin(BaseMixin):
    
    address: str
    city: Optional[str] = None
    commune: Optional[str] = None
    postal_code: Optional[int] = None

    def __str__(self) -> str:
        return f'{self.address}{(" ," + self.commune) if self.commune else ""}'