import os
from sys import modules
from inspect import isclass
from importlib import import_module
from typing import Any, Callable, Generator

from flask import Blueprint
from flask_sqlalchemy import Model # No error!
from config import BASEDIR

import logging

# main project path & module name ---------------------------------------------
APP_MODULE = os.getenv('APP_MODULE', 'app')
APP_DIR = os.path.join(BASEDIR, APP_MODULE)


def get_modules(module: str, include_init: bool = False) -> Generator[str, str, None]:
    """Returns all .py modules in given `module` directory that are not `__init__`.
    If include_init is `True` then the `__init__.py` file is taked in count.
        
    Usage:
        get_modules('models')

    Yields dot-notated module paths for discovery/import.
    Example:
      /proj/app/models/foo.py > app.models.foo
    """

    file_dir = os.path.abspath(os.path.join(APP_DIR, module))
    logging.debug(f'Getting modules at: {file_dir}')
    for root, _, files in os.walk(file_dir):
        mod_path = '{}{}'.format(APP_MODULE, root.split(APP_DIR)[1]).replace('/', '.').replace('\\', '.')
        for filename in files:
            if include_init and filename.endswith('.py'):
                yield '.'.join([mod_path, filename[0:-3]])
            if filename.endswith('.py') and not filename.startswith('__init__'):
                yield '.'.join([mod_path, filename[0:-3]])

    return None


def dynamic_loader(module_name: str, compare: Callable[[Any], bool], include_init: bool = False) -> list[Any]:
    """Iterates over all .py files in `module` directory, finding all classes that
    match `compare` function.
    Other classes/objects in the module directory will be ignored.

    Returns unique list of matches found.
    """
    items = []
    logging.debug(f'Loading dynamicly at: {module_name} module')
    for mod in get_modules(module_name, include_init):
        logging.debug(f'Module: {mod} is been imported')
        module = import_module(mod)
        if hasattr(module, '__all__'):
            objs = [getattr(module, obj) for obj in module.__all__] # type: ignore
            items += [o for o in objs if compare(o) and o not in items]
    return items


def get_models() -> list[Model]:
    """Dynamic model finder."""
    return dynamic_loader('models', is_model)


def is_model(item: Any) -> bool:
    """Determines if `item` is a `db.Model`."""
    return isclass(item) and issubclass(item, Model) and not item.__ignore__()


def load_models() -> None:
    """Load application models for management script & app availability."""
    logging.info(f'Loading models...')
    models = get_models()
    for model in models:
        setattr(modules[__name__], model.__name__, model)
        logging.debug(f'Model {model.__name__} loaded..')
    logging.info(f'[{len(models)}] Models loaded')


def get_blueprints() -> list[Blueprint]:
    """Dynamic blueprint finder."""
    return dynamic_loader('blueprints', is_blueprint, include_init=True)


def is_blueprint(item) -> bool:
    """Determine if `item` is a `Blueprint` instance
    (because we don't want to register `Blueprints` itself).
    """
    return isinstance(item, Blueprint)  # and not item.__ignore__()