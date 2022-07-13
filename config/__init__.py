from pickle import FALSE
from typing import Literal
import os


BASEDIR = os.path.split(os.path.abspath(os.path.dirname(__file__)))[0]
APP_NAME = os.environ.get("APP_NAME", "app").lower()


class Config:
    """Base configuration object."""
    # ---------- Platform Information
    APP_NAME = os.environ.get("APP_NAME", "app").lower()
    APP_DOMAIN = os.environ.get('APP_DOMAIN', 'app.com')
    APP_ADMIN = os.environ.get('APP_ADMIN', 'seba.salinas.delrio@gmail.com')
    # ---------- Flask-Mailing Configuration
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'Username')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'Password')
    MAIL_PORT = os.environ.get('MAIL_PORT') or 587
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_FROM = f'administracion@{APP_DOMAIN}'
    MAIL_FROM_NAME = os.environ.get('APP_NAME')
    DONT_REPLY_MAIL_FROM = f'error@{APP_DOMAIN}'
    
    
    # ---------- Flask Secret Key
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'Really Hard Password')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


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
