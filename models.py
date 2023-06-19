from typing import Any, Type
from flask_login import UserMixin
from sqlalchemy import String, create_engine, ForeignKey
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy import types
from conf import SQLALCHEMY_DATABASE_URI
from enum import IntEnum, Enum
# Session = sessionmaker(bind=engine)

engine = create_engine(SQLALCHEMY_DATABASE_URI)


class UserRoles(IntEnum):
    admin = 0
    reporter = 1
    city = 2
    spectator = 3

class Base(DeclarativeBase):
    pass

class EnumCol(types.TypeDecorator):

    impl = types.INTEGER

    def __init__(self,enum_type:Type[Enum], *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self._enum_type = enum_type

    def process_bind_param(self, value: Any | None, dialect: Dialect) -> Any:
        if isinstance(value,int):
            return value
        else:
            raise TypeError
        
    def process_result_value(self, value: Any | None, dialect: Dialect) -> Any | None:
        return self._enum_type(value)



class User(Base, UserMixin):

    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[EnumCol] = mapped_column(EnumCol(UserRoles), nullable=False, default=UserRoles.reporter)
    google_id: Mapped[int] = mapped_column(nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)

    user_detail: Mapped["UserDetail"] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return '<User {}>'.format(self.email)

class UserDetail(Base):
    
    __tablename__ = "user_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{User.__tablename__}.id"))
    profile_pic: Mapped[str] = mapped_column(nullable=True)
    g_email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="user_detail")
    