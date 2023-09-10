import os
from flask import Flask, Response, g
from flask_login import LoginManager
from flask_session import Session # type: ignore
from dotenv import load_dotenv
from flask_socketio import SocketIO, send
# from flask.sessions import SecureCookieSessionInterface, SessionMixin

from .exceptions import AppBaseException, ApiException

login_manager = LoginManager()
session = Session()
socketio = SocketIO()

def create_app():
    app = Flask(__name__,instance_relative_config=True)
    load_dotenv(f"{app.instance_path}/.env")
    env = os.environ["FLASK_ENV"]
    # Stupidly, importing from the instance folder needs a dot notation of the instance
    # folder name
    app.config.from_object(f"instance.conf.{env}Conf")

    # bcrypt = Bcrypt(app)
    login_manager.init_app(app)
    session.init_app(app)
    socketio.init_app(app,cors_allowed_origins=app.config["FRONTEND_ADDRESS"])

    with app.app_context():
        from .routes import routes
        app.register_blueprint(routes)
    
    @app.errorhandler(AppBaseException)
    def handle_errors(e):
        if isinstance(e, ApiException):
            # TODO: Remove the following and add the logger
            print(e.reason)
            return {
                "error": e.message
            }, 404
        else:
            return {
                "error": "Unknown App Error"
            }, 500
                
    @app.teardown_appcontext
    def tear_down(_):
        if 'db_session' in g:
            db_session = g.pop('db_session')
            db_session.close()

    return app,socketio