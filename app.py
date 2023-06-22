from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_pyfile("conf.py")
bcrypt = Bcrypt(app)

with app.app_context():
    from routes import routes
    app.register_blueprint(routes)