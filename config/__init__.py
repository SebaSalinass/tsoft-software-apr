from typing import Literal
import os


BASEDIR = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
APP_NAME = os.environ.get("APP_NAME", "app").lower()


class Config:
    """Base configuration object."""
    # ---------- Platform Information
    APP_NAME = os.environ.get("APP_NAME", "app").lower()
    # ---------- Flask Secret Key
    SECRET_KEY = os.environ.get('SECRET_KEY', 'Really Hard Password')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SUPPRESS_SEND = 1
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL', 'sqlite:///' + \
                                             os.path.join(BASEDIR, f'database/{APP_NAME}.sqlite'))


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SERVER_NAME = 'localhost'
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL', 'sqlite://')


class ProductionConfig(Config):
    """Production configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('APP_DATABASE_URL')


CONFIG = Literal['development', 'testing', 'production', 'default']
config: dict[str, Config] = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
}
