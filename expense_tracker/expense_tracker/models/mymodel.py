from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    DateTime
)

from .meta import Base


class Expense(Base):
    __tablename__ = 'expense'
    id = Column(Integer, primary_key=True)
    title = Column(Unicode)
    price = Column(Integer)
    paid_date = Column(DateTime)
    description = Column(Unicode)
