import requests
from flask import Blueprint, current_app, redirect, request, Request
from oauthlib.oauth2 import WebApplicationClient
from flask_login import LoginManager, login_required
import os


from .references import GoogleDiscoveryKeys, GoogleAuthResponse
from .controller import create_litter_report, get_user_by_jwt_token, conventional_user_auth, google_user_auth_or_create, invalidate_token
from .exceptions import CrudError, IncompleteParams

routes = Blueprint('routes', __name__, url_prefix="/api")
oauth_client = WebApplicationClient(os.environ["GOOGLE_CLIENT_ID"])
assert os.getenv("GOOGLE_CLIENT_SECRET") is not None
google_provider_cfg = requests.get(os.environ["GOOGLE_DISCOVERY_URL"]).json()
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(current_app)


@routes.route('/')
def index():
    return {
        "result": "Yo"
    } , 200


@routes.route("/g-auth")
def g_auth():
    authorization_endpoint = google_provider_cfg[GoogleDiscoveryKeys.AUTH_ENDPOINT]
    request_uri = oauth_client.prepare_request_uri(
        uri=authorization_endpoint,
        redirect_uri=f"{request.base_url}/callback",
        scope=["openid", "email", "profile"]
    )
    print(request_uri)
    return redirect(request_uri)

@routes.route("/g-auth/callback")
def g_auth_callback():
    auth_code = request.args.get("code")
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

    parse_res = oauth_client.parse_request_body_response(token_response.content)
    print(parse_res)

    userinfo_endpoint = google_provider_cfg[GoogleDiscoveryKeys.USERINFO_ENDPOINT]

    url, headers, body = oauth_client.add_token(uri=userinfo_endpoint)

    userinfo_response = requests.get(url=url, headers=headers, data=body)

    g_auth_response = GoogleAuthResponse(**userinfo_response.json())
    token = google_user_auth_or_create(g_auth_response)
    return {
        "api_token": token
    }, 200



@routes.post(rule="/test-g-auth")
def test_g_auth():
    g_auth_response = GoogleAuthResponse(**request.get_json())
    token = google_user_auth_or_create(g_auth_response)
    return {
        "api_key": token
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
        "api_key": token
    }, 200


@routes.post("/report-littering")
@login_required
def report_littering():
    #TODO: Validate the request also remove the api_key
    payload = request.get_json()
    del payload['api_key']
    try:
        create_litter_report(**payload)
    except:
        raise CrudError(
            message="Report cannot be created", 
            reason="report creation error"
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


@login_manager.request_loader
def load_user_from_request(request):
    api_key = get_token_from_request(request)
    if api_key:
        return get_user_by_jwt_token(token=api_key)
    # finally, return None if both methods did not login the user
    return None

def get_token_from_request(request: Request):
    if request.method == "GET":
        api_key = request.args.get('api_key')
    elif request.method == "POST" and request.is_json:
        api_key = request.get_json().get('api_key')
    else:
        raise ValueError
    return api_key
