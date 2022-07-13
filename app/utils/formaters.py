from typing import SupportsInt
from arrow import Arrow


def _M(money: SupportsInt[int, str, float], no_sign: bool = False) -> str:
    """Formats an integer convertible, to thousand dotted string type.

    Args:
        money (SupportsInt[int, str, float]): money quantity. int must be callable on it.
        no_sign (bool, optional): Hides the `$` sign. Defaults to False.

    Returns:
        str: The Formated String
    
    Example:
        >>> _M(20_000)
        >>> '$20.000'
        >>> _M('40_000', no_sign=True)
        >>> '40.000'
    """
    return f'{["$",""][no_sign]}{int(money):,}'.replace(',', '.')


def _T(time: Arrow, short: bool = False, verbose: bool = False, tzone: str = 'America/Santiago') -> str:
    """Formats an Arrow object

    Args:
        time (Arrow): The Arrow instance to format.
        short (bool, optional): Hides hours and minutes. Defaults to False.
        verbose (bool, optional): Adds literal conectors to the string. Defaults to False.
        tzone (str, optional): Tzone to transform the time. Defaults to 'America/Santiago'.

    Returns:
        str: Formated string
        
    Example:
        >>> date = Arrow(2022, 1, 1, 20, 30)
        >>> _T(date)
        >>> '01-01-2022 20:30'
        >>> _T(date, verbose=True)
        >>> '01 de Enero del 2022'
    """
    fmt_date = ['DD-MM-YYYY', 'DD [X] MMMM [Y] YYYY'][verbose]
    fmt_time = ['HH:mm', '[a las] HH:mm'][verbose]
    fmt = f'{fmt_date} {fmt_time if not short else ""}'.strip()

    return time.to(tzone).format(fmt, locale='es').title().replace('X', 'de').replace('Y', 'del')


def _R(rut: str) -> str:
    """Chilean rut string formater

    Args:
        rut (str): The given rut

    Returns:
        str: The formated rut string.
    """
    clean_rut = rut.replace('.', '').replace('*', '').replace('-', '')
    rut, dv = clean_rut[0:-1], clean_rut[-1]
    return f'{int(rut):,}-{dv}'.replace(',', '.')
