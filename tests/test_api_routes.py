from flask.testing import FlaskClient
from src.models import User
import json

def test_root(client: FlaskClient):
    response = client.get("api/")
    assert response.status_code == 200
    assert response.json

def test_auth(user:User, client:FlaskClient):
    request = {
        'email': user.email,
        'password': '123456'
    }
    response = client.post("api/auth",json=request)
    assert response.status_code == 200
    assert response.json




