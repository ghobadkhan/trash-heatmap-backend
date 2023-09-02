from typing import Literal
from flask import Flask
from flask.app import Flask
from flask_login import LoginManager
from dotenv import load_dotenv
# from flask.sessions import SecureCookieSessionInterface, SessionMixin

from .exceptions import AppBaseException, ApiException

login_manager = LoginManager()

def create_app(env:Literal['Dev','Test','Prod'] = 'Dev'):
    app = Flask(__name__,instance_relative_config=True)
    # Stupidly, importing from the instance folder needs a dot notation of the instance
    # folder name
    app.config.from_object(f"instance.conf.{env}Conf")

    # bcrypt = Bcrypt(app)
    login_manager.init_app(app)
    load_dotenv(f"{app.instance_path}/.env")

    with app.app_context():
        from .routes import routes
        app.register_blueprint(routes)

    @app.errorhandler(AppBaseException)
    def handle_errors(e):
        if isinstance(e, ApiException):
            return {
                "error": e.message
            }, 404
        else:
            return {
                "error": "Unknown App Error"
            }, 500
    return app