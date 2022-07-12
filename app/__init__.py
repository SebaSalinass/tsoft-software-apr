from flask import Flask
from config import config, CONFIG


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

    return app
