import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin
from .db_session import SqlAlchemyBase


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    author = sa.Column(sa.String)
    genre = sa.Column(sa.String)
    publisher = sa.Column(sa.String)
    title = sa.Column(sa.String)
    publication_year = sa.Column(sa.Integer)
    total_copies = sa.Column(sa.Integer)
    available_copies = sa.Column(sa.Integer)
    location = sa.Column(sa.String)

    loans = orm.relationship('Loan', back_populates='book')
    reservations = orm.relationship('Reservation', back_populates='book')
