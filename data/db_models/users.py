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
    is_admin = sa.Column(sa.Integer, default=0)
    is_active = sa.Column(sa.Integer, default=1)
    created_at = sa.Column(sa.DateTime)

    loans = orm.relationship('Loan', backref='reader', cascade="all, delete-orphan")
    reservations = orm.relationship('Reservation', backref='reader', cascade="all, delete-orphan")

    @property
    def active_loans(self):
        """Активные выдачи книг"""
        return [loan for loan in self.loans if loan.status in ['active', 'overdue']]

    @property
    def overdue_loans(self):
        """Просроченные книги"""
        return [loan for loan in self.loans if loan.status == 'overdue']
