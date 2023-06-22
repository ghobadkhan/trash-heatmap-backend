from typing import Any, List, Optional, Type
from flask_login import UserMixin
from flask_bcrypt import Bcrypt
from sqlalchemy import String, create_engine, ForeignKey, NUMERIC
from sqlalchemy.dialects.postgresql import SMALLINT, TIMESTAMP
from sqlalchemy.engine.interfaces import Dialect
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy.orm.base import Mapped
from sqlalchemy import types
from sqlalchemy.ext.hybrid import hybrid_property
from conf import SQLALCHEMY_DATABASE_URI
from enum import IntEnum, Enum
from datetime import datetime

engine = create_engine(SQLALCHEMY_DATABASE_URI)
# Session = sessionmaker(bind=engine)


class UserRole(IntEnum):
    admin = 0
    reporter = 1
    city = 2
    spectator = 3

class UserReportStatus(IntEnum):
    pending = 0
    open = 1
    closed = 2
    rejected = 3

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
    cryptor: Bcrypt

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    _password: Mapped[bytes] = mapped_column(String(128), nullable=True)
    role: Mapped[EnumCol] = mapped_column(EnumCol(UserRole), nullable=False, default=UserRole.reporter)
    google_id: Mapped[int] = mapped_column(nullable=True, unique=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=True)
    last_name: Mapped[str] = mapped_column(String(50), nullable=True)

    @hybrid_property
    def password(self) -> Optional[bytes]:
        return self._password

    @password.inplace.setter
    def _set_password(self, value) -> None:
        if type(value) != str:
            raise TypeError("Password must be provided in plain text")
        self._password = self.cryptor.generate_password_hash(value)
    

    detail: Mapped["UserDetail"] = relationship(back_populates="user", cascade="all, delete-orphan")
    reports: Mapped[List["UserReport"]] = relationship(back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return '<User {}>'.format(self.email)

class UserDetail(Base):
    
    __tablename__ = "user_details"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{User.__tablename__}.id"))
    profile_pic: Mapped[str] = mapped_column(nullable=True)
    g_email_verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="detail")


class UserReport(Base):
    __tablename__ = "user_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey(f"{User.__tablename__}.id"))
    last_status: Mapped[EnumCol] = mapped_column(EnumCol(UserReportStatus), default=UserReportStatus.pending)
    lat: Mapped[float] = mapped_column(NUMERIC(precision=8,scale=6), nullable=False)
    lng: Mapped[float] = mapped_column(NUMERIC(precision=8,scale=6), nullable=False)
    radius: Mapped[int] = mapped_column(SMALLINT(), nullable=False, default=3)
    count: Mapped[int] = mapped_column(SMALLINT(),nullable=False, default=1)
    comment_ref_id: Mapped[str] = mapped_column(String(24), nullable=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(),nullable=False, default=datetime.now())

    user: Mapped["User"] = relationship(back_populates="reports")

    