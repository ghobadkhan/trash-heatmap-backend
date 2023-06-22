from sqlalchemy import select
from sqlalchemy.orm import Session
from typing import Optional, Iterable
from flask_bcrypt import Bcrypt
from flask import current_app

from models import Base, User, engine

session = Session(engine)

def create_all_tables():
    Base.metadata.create_all(engine)

def drop_all_tables():
    Base.metadata.drop_all(engine)

def get_user_by_id(id:int):
    stmt = select(User).where(User.id == id)
    return session.scalars(stmt).first()

def create_user(first_name:str, last_name:str, email:str,
                 password: Optional[str] = None, google_id: Optional[int] = None):
    
    User.cryptor = Bcrypt(current_app)
    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    
    if password is None and google_id is None:
        raise ValueError("User must either have password or a google account")
    
def db_commit(*models: Iterable[Base]):
    with Session(bind=engine) as session:
        session.add_all(models)
        session.commit()