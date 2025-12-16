from datetime import datetime, timedelta

import sqlalchemy as sa
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .books import Book
from .db_session import SqlAlchemyBase
from .users import User


class Loan(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'loans'

    id = sa.Column(sa.Integer,
                   primary_key=True, autoincrement=True)
    reader_id = sa.Column(sa.Integer, sa.ForeignKey(User.id))
    book_id = sa.Column(sa.Integer, sa.ForeignKey(Book.id))
    loan_date = sa.Column(sa.Date)
    due_date = sa.Column(sa.Date)
    return_date = sa.Column(sa.Date)
    status = sa.Column(sa.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.due_date:
            self.due_date = datetime.now() + timedelta(days=14)

    @property
    def is_overdue(self):
        if self.status in ['returned', 'cancelled']:
            return False
        return datetime.now() > self.due_date

    def check_overdue(self):
        """Проверяет, просрочена ли книга"""
        if self.is_overdue and self.status == 'active':
            self.status = 'overdue'
            return True
        return False
