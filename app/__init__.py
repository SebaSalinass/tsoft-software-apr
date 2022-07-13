from logging.config import dictConfig
from flask import Flask

from config import config, CONFIG
from config.logger import setup_logging_dict

from .db import init_db, db, shutdown_session
from .extensions import login_manager
from .models.user import user_loader


def create_app(cfg_setting: CONFIG = 'default') -> Flask:
    """Flask app factory

    Args:
        cfg_setting (CONFIG, optional): Configuration that the Flask app will use.
        Defaults to 'default'.

    Returns:
        Flask: The app itself.
    """

    app = Flask(__name__)
    app.config.from_object(config[cfg_setting])
    # ---------- Configuring Enviroment
    cfg = app.config
    app.env = cfg.get('FLASK_ENV', 'development')
    app.logger.info(f'Current app enviroment: [{app.env.upper()}]')
    
    # ---------- Configuring Logging
    dictConfig(setup_logging_dict(app))
    app.logger.debug(f'Logging Configured')
    
    login_manager.init_app(app)
    login_manager.user_loader(user_loader)
    
    init_db(app, db)
    app.teardown_appcontext_funcs.append(shutdown_session)
    app.logger.info('Database initialized.')
    
    # --------- Extension Initialization 
    login_manager.init_app(app)
    
    return app
