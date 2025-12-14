import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    full_name = sa.Column(sa.String)
    email = sa.Column(sa.String, index=True, unique=True)
    birthday = sa.Column(sa.Date)
    hashed_password = sa.Column(sa.String)
    salt = sa.Column(sa.String)
    admin = sa.Column(sa.Integer, default=0)

    loans = orm.relationship('Loan', back_populates='user', cascade="all, delete-orphan")
    reservations = orm.relationship('Reservation', back_populates='user', cascade="all, delete-orphan")
