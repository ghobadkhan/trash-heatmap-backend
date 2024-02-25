from flask.testing import FlaskClient
from src.app.models import User
import os

def test_env(app):
    assert os.environ["FLASK_ENV"] == 'Test'

# def test_root(client: FlaskClient):
#     response = client.get("api/")
#     assert response.status_code == 200
#     assert response.json

def test_auth(user:User, client:FlaskClient):
    request = {
        'email': user.email,
        'password': '123456'
    }
    response = client.post("api/auth",json=request)
    assert response.status_code == 200
    assert response.is_json

def test_report_litter(user:User, client:FlaskClient):
    request = {
        "lat": 39.2344,
        "lng": 20.543,
        "count": 666,
        "comment": "Sooo fucking disgusting!"
    }
    headers = {
        "api_token": user.remember_token
    }
    response = client.post("api/report-littering",json=request, headers=headers)
    assert response.status_code == 200
    assert response.is_json

def test_logout(user:User, client:FlaskClient):
    headers = {
        "api_token": user.remember_token
    }

    response = client.get("api/logout",headers=headers)
    assert response.status_code == 200
    assert user.remember_token is None


def test_session(client:FlaskClient):
    name = "test_anon"
    response = client.get("api/test", query_string={"name":name})
    assert response.status_code == 200
    response = client.get("api/test/get-session")
    assert response.is_json
    data = response.get_json()
    assert data["name"] == name
    
