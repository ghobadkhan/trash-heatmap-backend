import requests
from flask import Blueprint, current_app, make_response, jsonify, redirect, request, url_for
from base64 import b16encode
from oauthlib.oauth2 import WebApplicationClient
from flask_login import LoginManager, login_required, logout_user

from env import GOOGLE_CLIENT_ID, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_SECRET
from references import GoogleDiscoveryKeys
from controller import get_user_by_id

routes = Blueprint('routes', __name__, url_prefix="/api")
oauth_client = WebApplicationClient(GOOGLE_CLIENT_ID)
google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(current_app)


@routes.route('/')
def index():
    return {
        "result": "Yo"
    } , 200

@routes.route('/get-session')
def get_session():
    secret_bytes = current_app.config.get("SECRET_KEY")
    assert secret_bytes
    response = make_response(jsonify({"session_secret":b16encode(secret_bytes).decode('utf-8')}), 200)
    response.set_cookie("name","something")
    return response

@routes.route("/login")
def login():
    authorization_endpoint = google_provider_cfg[GoogleDiscoveryKeys.AUTH_ENDPOINT]
    request_uri = oauth_client.prepare_request_uri(
        uri=authorization_endpoint,
        redirect_uri=f"{request.base_url}/callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@routes.route("login/callback")
def login_callback():
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
        auth=(GOOGLE_CLIENT_ID,GOOGLE_CLIENT_SECRET)
    )

    parse_res = oauth_client.parse_request_body_response(token_response.content)
    print(parse_res)

    userinfo_endpoint = google_provider_cfg[GoogleDiscoveryKeys.USERINFO_ENDPOINT]

    url, headers, body = oauth_client.add_token(uri=userinfo_endpoint)

    userinfo_response = requests.get(url=url, headers=headers, data=body)

    return userinfo_response.json(), 200

@login_required
@routes.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("/"))

@login_manager.user_loader
def load_user(id:int):
    return get_user_by_id(id)
