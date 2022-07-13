import re
from itertools import cycle
from typing import Literal, Union


def validate_rut(rut: str) -> bool:
    """
    Validates a RUT type string, cleaning dots and other characters
    Return `True` if a valid verification digit corresponds to the given RUT
    """

    if re.match(r'^(\d{1,3})([\.\*]?(\d{3}))([\.\*]?(\d{3}))[-*]([\dkK])$', rut):
        # CLEANING RUT
        clean_rut = rut.replace('.', '').replace('*', '').replace('-', '')
        rut, verification_code = str(clean_rut[0:-1] + '-' + clean_rut[-1]).split('-')
        
        # VERIFICATION CODE FOR RUT
        reversed_digits = map(int, reversed(str(rut)))
        factors = cycle(range(2, 8))
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        code = (-s) % 11
        
        # RETURNING IF GIVEN VERIFICATION CODE == CODE
        if code > 10 and verification_code == '0':
            return True
        elif code == 10 and verification_code.lower() == 'k':
            return True
        elif str(code) == verification_code:
            return True
        else:
            return False

    return False

def validate_user_name(name: str) -> bool:    
    if re.match(r'^(?![\s.]+$)[a-zA-Z\s.áéíóúñÁÉÍÓÚÑ]{2,20}$', name):
        return True
    return False

def validate_business_name(name: str) -> bool:    
    if re.match(r'^(?![\s.]+$)[a-zA-Z0-9\s$-/:-?{-~!"^_`\[\].áéíóúñÁÉÍÓÚÑ]{1,100}$', name):
        return True
    return False

def validate_email(email: str) -> bool: 
    if re.match(r'^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$', email, re.IGNORECASE):
        return True
    return False

def valid_phone(phone: Union[str, int]) -> Union[Literal[False], str]:

    if match := re.match(r'^(\+?56)?(\s?)(0?9)(\s?)[9876543]\d{7}$', str(phone)):
        code = match.group(3)
        number = str(phone)
        prefix = f'+56{code}'
        number = number[len(number) - 8:]
        return prefix + number

    return False

def validate_file_extensions(filename, extensions) -> bool:    
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in extensions
