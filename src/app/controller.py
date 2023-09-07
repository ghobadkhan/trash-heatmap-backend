import jwt
from sqlalchemy import select, create_engine
from sqlalchemy.orm import Session
from typing import Optional, cast
from flask_login import login_user, current_user
from flask import has_app_context, current_app,g
from datetime import datetime, timedelta
from pymongo import MongoClient
from werkzeug.local import LocalProxy

from .models import Base, User, UserDetail, UserReport
from .exceptions import UserAuthError
from .references import GoogleAuthResponse
from ..utils import get_config

engine = create_engine(current_app.config["SQLALCHEMY_DATABASE_URI"])

def get_db_session():
    if 'db_session' not in g:
        g.db_session = Session(engine)
    return g.db_session

session = cast(Session,LocalProxy(get_db_session))

mongo_client: MongoClient = MongoClient('localhost', 27017)
#In mongodb, a database (db_name) is called/created using just mongo_client.db_name
mongo_db = mongo_client.trash_heat
comment_collection = mongo_db.user_comments

def create_all_tables(engine=engine):
    Base.metadata.create_all(engine)

def drop_all_tables(engine=engine):
    Base.metadata.drop_all(engine)

def get_user_by_email(email:str) -> User | None:
    stmt = select(User).filter(User.email == email)
    return session.scalar(stmt)
    
def create_user(
        email:str,
        first_name:Optional[str] = None, 
        last_name:Optional[str] = None,
        passwd: Optional[str] = None, 
        google_id: Optional[str] = None,
        detail: Optional[UserDetail] = None
    ):
    
    user = User(first_name=first_name, last_name=last_name, email=email)
    if passwd:
        user.password = passwd
    elif google_id:
        user.google_id = google_id
    else:
        raise ValueError("User must either have password or a google account")
    if detail:
        user.detail = detail
    db_commit(user)
    return user

def google_user_auth_or_create(g_auth_response:GoogleAuthResponse):
    if not g_auth_response.email_verified:
        raise UserAuthError(
            reason="gmail is not verified",
            message="Sorry, you must have a verified Gmail account!"
        )
    user = get_user_by_email(g_auth_response.email)
    if not user:
        user = create_user(
            email=g_auth_response.email,
            first_name=g_auth_response.given_name,
            last_name=g_auth_response.family_name,
            google_id=g_auth_response.sub,
            detail= UserDetail(
                profile_pic = g_auth_response.picture,
                gmail_verified = g_auth_response.email_verified
            )
        )
        user = get_user_by_email(g_auth_response.email)
    elif user.google_id != g_auth_response.sub:
        raise UserAuthError(
            reason="google unique id mismatch",
            message="There's a mismatch of your current Google user info and saved info"
        )
    if user:
        return create_token_login(user)
    else:
        raise UserAuthError(reason="empty user returned after auth", message="Internal Error")
    
def create_user_detail(g_email_verified:bool | None = None, profile_pic: str | None = None):
    return UserDetail(g_email_verified=g_email_verified, profile_pic=profile_pic)

def encode_auth_token(user_id:int):
        """
        Generates the Auth Token
        :return: string
        """
        # TODO: Add debug/test condition
        
        payload = {
                'exp': datetime.utcnow() + timedelta(days=0, seconds=600),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
        return jwt.encode(
            payload,
            get_config('SECRET_KEY'),
            algorithm='HS256'
        )
        
def decode_auth_token(auth_token:str):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(jwt=auth_token, key=get_config('SECRET_KEY'),algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        raise UserAuthError(
            message="Signature expired. Please log in again.",
            reason="jwt expire"
        )
    except jwt.InvalidTokenError:
        raise UserAuthError(
            message="Invalid token. Please log in again.",
            reason="jwt invalid"
        )
    
def get_user_by_jwt_token(token:str):
    user_id = decode_auth_token(token)
    stmt = select(User).filter(User.id == user_id)
    user = session.scalar(stmt)
    if user is None or user.remember_token != token:
        raise UserAuthError(
            message="Invalid token. Please log in again.",
            reason="jwt invalid"
        )
    return user

def conventional_user_auth(email:str, password:str):
    user = get_user_by_email(email)
    if not user:
        raise UserAuthError(reason="email not found")
    if not user.password_matches(password):
        raise UserAuthError(reason="password not found")
    return create_token_login(user)

def create_token_login(user:User):
    token = encode_auth_token(user.id)
    user.remember_token = token
    db_commit(user)
    if has_app_context():
        login_user(user)
    else:
        print("Debugging")
    return token

def invalidate_token():
    user = cast(User,current_user)
    user.remember_token = None
    db_commit(user)

def create_litter_report(lat:float, lng:float, count:int=1, comment:str | None = None):
    user = cast(User,current_user)
    #TODO: Basic sanitization
    comment_ref_id = None
    if comment is not None:
        result = comment_collection.insert_one({
            "user_id": user.id,
            "type": "trash_report",
            "body": comment
        })
        comment_ref_id = str(result.inserted_id)

    user.reports.append(
        UserReport(lat=lat, lng=lng, count=count, comment_ref_id= comment_ref_id)
    )
    db_commit(user)
    

def db_commit(*models: Base):
    session.add_all(models)
    session.commit()