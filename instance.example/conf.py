import os
# This file configures the server based on the running environment that's set in .env
class Config(object):
    TESTING = False
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_COOKIE_NAME = "server_session"
    SESSION_COOKIE_SECURE = True
    SESSION_USE_SIGNER = True
    SESSION_COOKIE_HTTPONLY = False
    # 'Strict' or 'Lax' or None (default)
    SESSION_COOKIE_SAMESITE = 'Strict'
    FRONTEND_ADDRESS = "https://localhost:4200"

class DevConf(Config):
    TESTING = True
    SECRET_KEY = b'THIS_IS_A_DEV'
    FLASK_ENV = "development"
    SQLALCHEMY_DATABASE_URI= 'postgresql+psycopg2://<user>:<pass>@localhost/trash_heat'

class TestConf(Config):
    TESTING = True
    SECRET_KEY = b'THIS_IS_A_TEST'
    FLASK_ENV = "test"
    SQLALCHEMY_DATABASE_URI= 'postgresql+psycopg2://<user>:<pass>@0.0.0.0:10000/test_trash_heat'

class ProdConf(Config):
    TESTING = False
    SECRET_KEY = os.urandom(16)
    FLASK_ENV = "deployment"
    SQLALCHEMY_DATABASE_URI= 'postgresql+psycopg2://<user>:<pass>@localhost/trash_heat'

# SESSION_REFRESH_EACH_REQUEST = False
# DEBUG = True --> No use. DEBUG value can only be set at run command using --debug