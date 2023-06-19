from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Base, User, engine

session = Session(engine)

def create_all_tables():
    Base.metadata.create_all(engine)

def drop_all_tables():
    Base.metadata.drop_all(engine)

def get_user_by_id(id:int):
    stmt = select(User).where(User.id == id)
    return session.scalars(stmt).first()