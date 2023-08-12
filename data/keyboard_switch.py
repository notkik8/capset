import sqlalchemy
from .db_session import SqlAlchemyBase


class Switch(SqlAlchemyBase):
    __tablename__ = 'switch'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    image_url = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    price = sqlalchemy.Column(sqlalchemy.Float, nullable=True)

    def __repr__(self):
        return f"<Product(name='{self.name}', price={self.price})>"
