from typing import Optional
from uuid import UUID


import jwt
from arrow import utcnow
from bcrypt import hashpw, gensalt, checkpw


class AuthMixin():
    
    id: Optional[UUID]
    password_hash: bytes

    
    @property
    def password(self) -> AttributeError:
        raise AttributeError('Password is not a readable attribute')

    @password.setter
    def password(self, value: str) -> None:
        self.password_hash = hashpw(
            bytes(value, encoding='utf-8'), gensalt(10))
        
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def get_id(self) -> str:
        return str(self.id)

    def verify_password(self, password: str) -> bool:
        '''Checks if given `password` argument matchs `password_hash`'''
        return checkpw(bytes(password, encoding='utf-8'), self.password_hash)

    def token_password_reset(self, secret_key: str, exp_hours: int = 2) -> str:
        assert isinstance(secret_key, str) and isinstance(exp_hours, int)
        
        data = {
            'exp': utcnow().shift(hours=exp_hours).datetime,
            'user_id': str(self.id),
            'password_hash': str(self.password_hash)
        }

        return jwt.encode(data, secret_key)
    
    @classmethod
    def validate_reset_password_token(cls, secret_key: str, token: str) -> Optional[UUID]:
        
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
        except Exception as e:
            # TODO LOGGING HERE
            return False
        
        return UUID(data['user_id'])
    
    def token_email_reset(self, email: str, secret_key: str, exp_seconds: int = 60**2*2) -> str:
        assert isinstance(secret_key, str) and isinstance(exp_seconds, int)
        
        data = {
            'exp': utcnow().shift(seconds=exp_seconds).datetime,
            'user_id': str(self.id),
            'email': email, 
        }

        return jwt.encode(data, secret_key)
  
    def validate_reset_email_token(self, secret_key: str, token: str) -> Optional[str]:
        
        try:
            data = jwt.decode(token, secret_key, algorithms=['HS256'])
        except Exception as e:
            # TODO LOGGING HERE
            return False
        
        if data['user_id'] == str(self.id):
            return data['email']
    
        return False