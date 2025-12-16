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
    reserved_copies = sa.Column(sa.Integer, default=0)
    location = sa.Column(sa.String)

    loans = orm.relationship('Loan', backref='book', lazy=True, order_by='desc(Loan.loan_date)')
    reservations = orm.relationship('Reservation', backref='book', lazy=True,
                                    order_by='desc(Reservation.reservation_date)')

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def active_reservations(self):
        """Активные резервации книги"""
        return [res for res in self.reservations if res.status == 'pending']
