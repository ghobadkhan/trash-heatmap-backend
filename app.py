from flask import Flask

app = Flask(__name__)
app.config.from_pyfile("conf.py")


with app.app_context():
    from routes import routes
    app.register_blueprint(routes)