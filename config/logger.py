from flask.app import Flask

def setup_logging_dict(app: Flask) -> dict:
    
    if app.config['TESTING'] == True:
        level = 'CRITICAL'
        handlers = []
    elif app.config['ENV'] == 'development':
        level = 'DEBUG'
        handlers = ['console']
    elif app.config['ENV'] == 'production':
        level = 'INFO'
        handlers = ['console', 'error_file', 'email']
    else:
        raise EnvironmentError('Invalid environment for app state.')

    return {
        'version': 1,
        "disable_existing_loggers": True,
        "formatters": {
            "default": {
                "format": "[%(asctime)s] [%(levelname)s] [at %(module)s] : %(message)s",
            },
            "access": {
                "format": "%(message)s",
            },
            "email": {
                "format":
                    """
                    Application: {}
                    Emited at: [%(asctime)s]
                    Level: [%(levelname)s]
                    Module: [%(module)s]                    
                    Message:
                    %(message)s
                    """.format(app.config['APP_NAME']),
            },
        },
        "handlers": {
            "console": {
                "level": level,
                "class": "logging.StreamHandler",
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },

            "email": {
                "class": "logging.handlers.SMTPHandler",
                "formatter": "email",
                "level": "ERROR",
                "mailhost": (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                "fromaddr": app.config['MAIL_FROM'],
                "toaddrs": app.config['APP_ADMIN'],
                "subject": "An error has accured:",
                "credentials": (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD']),
                "secure": (),
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "default",
                "filename": "logs/errors.log",
                "maxBytes": 10000,
                "delay": "True",
            },
            "access_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "access",
                "filename": "/var/log/gunicorn.access.log",
                "maxBytes": 10000,
                "backupCount": 10,
                "delay": "True",
            }
        },
        "loggers": {
            "gunicorn.error": {
                "handlers": ["console"] if app.debug else ["console", "email"],
                "level": level,
                "propagate": False,
            },
            "gunicorn.access": {
                "handlers": ["console"] if app.debug else ["console", "email"],
                "level": level,
                "propagate": False,
            },
            "sqlalchemy": {
                "handlers": ["console"] if app.debug else ["console", "email"],
                "level": "WARNING",
                "propagate": False,
            },
            "werkzeug": {
                "handlers": ["console"] if app.debug else ["console", "email"],
                "level": "DEBUG",
                "propagate": False,
            },
            "alembic": {
                "handlers": ["console"] if app.debug else ["console", "email"],
                "level": "DEBUG",
                "propagate": False,
            }
        },
        "root": {
            "level": level,
            "handlers": handlers,
        }
    }
