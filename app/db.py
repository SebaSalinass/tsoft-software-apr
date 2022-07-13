from typing import Optional

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import force_auto_coercion

from .utils.loaders import load_models

# Our global DB object (imported by models & views & everything else)
# Session future option set to true to start using th new select approach on sqlalchemy 2.0
db = SQLAlchemy(session_options={'future': True})


def init_db(app: Flask, database: SQLAlchemy) -> None:
    """Initializes the global database object used by the app.

    Args:
        app (Flask): The Flask Application
        db (SQLAlchemy): The SQlalchemy Extension

    Raises:
        ValueError: If objects are not correct instances.
    """
    if isinstance(app, Flask) and isinstance(database, SQLAlchemy):
        force_auto_coercion()
        load_models()
        database.init_app(app)
    else:
        raise ValueError('Cannot init DB without db and app objects.')

def shutdown_session(exception: Optional[Exception] = None ) -> None:
    """Database shutdown session

    Args:
        exception (Optional[Exception], optional): Optional exception. Defaults to None.
    """
    db.engine.dispose()
    return
    