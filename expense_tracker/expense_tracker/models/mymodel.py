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

    def to_json(self):
        output = {}
        output['id'] = self.id
        output['title'] = self.title
        output['price'] = self.price
        output['paid_date'] = self.paid_date.strftime('%B %d, %Y')
        output['description'] = self.description
        return output
