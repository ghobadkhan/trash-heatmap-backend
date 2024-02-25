import os
import requests
from uuid import uuid1
from functools import wraps
from flask import (
    Blueprint,
    request,
    Request,
    session
    )
from oauthlib.oauth2 import WebApplicationClient
from flask_login import login_required

from .references import GoogleDiscoveryKeys, GoogleAuthResponse
from .controller import (
    create_litter_report, 
    get_user_by_jwt_token, 
    conventional_user_auth, 
    google_user_auth_or_create, 
    invalidate_token,
    )
from ..exceptions import CrudError, IncompleteParams
from . import socketio, login_manager
from ..data_structures import LitterForm

routes = Blueprint('routes', __name__, url_prefix="/api")
oauth_client = WebApplicationClient(os.environ["GOOGLE_CLIENT_ID"])
assert os.getenv("GOOGLE_CLIENT_SECRET") is not None
google_provider_cfg = requests.get(os.environ["GOOGLE_DISCOVERY_URL"]).json()

@login_manager.request_loader
def load_user_from_request(request):
    api_token = get_token_from_request(request)
    if api_token:
        return get_user_by_jwt_token(token=api_token)
    return None

def get_token_from_request(request: Request):
    return request.headers.get('api_token')

def is_env_test(func):
    @wraps(func)
    def inner(*args,**kwargs):
        assert os.getenv("FLASK_ENV") == "Test"
        return func(*args,**kwargs)
    return inner

@routes.get('/test')
@is_env_test
def index():
    name = request.args.get("name")
    if name is None:
        return {"response": "Name is empty"}, 400
    session["name"] = name
    return {"response": "OK"}, 200

@routes.get("/test/test-socket")
@is_env_test
def test_socket():
    ch = request.args.get("channel")
    socketio.emit(ch,"I got you!")
    return {"response": "OK"}, 200

@routes.get('/test/get-session')
@is_env_test
def get_session():
    name = session.get("name")
    return {"name": name}, 200


@routes.get("/g-auth")
def g_auth():
    user_state = uuid1()
    authorization_endpoint = google_provider_cfg[GoogleDiscoveryKeys.AUTH_ENDPOINT]
    request_uri = oauth_client.prepare_request_uri(
        uri=authorization_endpoint,
        redirect_uri=f"https://127.0.0.1:5000/api/g-auth/callback",
        scope=["openid", "email", "profile"],
        state=user_state
    )
    return {
        "response": "OK",
        "user_state": user_state,
        "redirect_uri": request_uri
    }, 200

@routes.get("/g-auth/callback")
def g_auth_callback():
    auth_code = request.args.get("code")
    user_state = request.args.get("state")
    assert auth_code is not None
    token_endpoint = google_provider_cfg[GoogleDiscoveryKeys.TOKEN_ENDPOINT]
    token_url, headers, body = oauth_client.prepare_token_request(
        token_url=token_endpoint,
        authorization_response= request.url,
        redirect_url=request.base_url,
        code=auth_code
    )

    token_response = requests.post(
        url=token_url,
        headers=headers,
        data=body,
        auth=(os.environ["GOOGLE_CLIENT_ID"],os.environ["GOOGLE_CLIENT_SECRET"])
    )

    oauth_client.parse_request_body_response(token_response.content)

    userinfo_endpoint = google_provider_cfg[GoogleDiscoveryKeys.USERINFO_ENDPOINT]

    url, headers, body = oauth_client.add_token(uri=userinfo_endpoint)

    userinfo_response = requests.get(url=url, headers=headers, data=body)

    g_auth_response = GoogleAuthResponse(**userinfo_response.json())
    token = google_user_auth_or_create(g_auth_response)
    print(f"sending info to: {user_state}")
    socketio.emit(
        user_state, 
        data={
        "response": "authenticated",
        "api_token": token
    })
    return {
        "response": "OK"
    }, 200



@routes.post(rule="/auth")
def auth():
    try:
        data = request.json
        assert data is not None, TypeError
        email = data['email']
        password = data['password']
        token = conventional_user_auth(email=email, password=password)
    except (KeyError, TypeError):
        raise IncompleteParams(
            reason="Missing email or password at auth",
            message="Email and/or password is missing"
            )
    return {
        "api_token": token
    }, 200


@routes.post("/report-litter")
@login_required
def report_littering():
    #TODO: Validate the request also remove the api_token
    form = LitterForm(**request.get_json())
    try:
        create_litter_report(form)
    except Exception as e:
        print(e)
        raise CrudError(
            message="Report cannot be created", 
            reason=str(e)
        )
    return {
        "message": "success"
    }, 200
    

@routes.get("/logout")
@login_required
def logout():
    invalidate_token()
    # return redirect(url_for("/"))
    return {
        "message": "Bye!"
    }, 200