from flask import Flask
from flask.app import Flask
from flask_bcrypt import Bcrypt
from flask.globals import g
from flask_login import LoginManager
from dotenv import load_dotenv
# from flask.sessions import SecureCookieSessionInterface, SessionMixin

from .exceptions import AppBaseException, ApiException


login_manager = LoginManager()

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile("conf.py")
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