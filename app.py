from flask import Flask
from flask.app import Flask
from flask_bcrypt import Bcrypt
from flask.globals import g
# from flask.sessions import SecureCookieSessionInterface, SessionMixin

from exceptions import AppBaseException, ApiException

app = Flask(__name__)
app.config.from_pyfile("conf.py")
bcrypt = Bcrypt(app)

# class CustomSession(SecureCookieSessionInterface):
#     def should_set_cookie(self, app: Flask, session: SessionMixin) -> bool:
#         return super().should_set_cookie(app, session)

def get_crypt():
    if 'crypt' not in g:
        g.crypt = Bcrypt(app)

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

with app.app_context():
    from routes import routes
    app.register_blueprint(routes)

if __name__ == "__main__":
    app.run(debug=True, ssl_context='adhoc')