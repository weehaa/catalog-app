from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import crud

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def items(self):
        return crud.items_bycat(self.name)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                'name': self.name,
                'id': self.id,
                'items': [i.serialize for i in self.items],
                }


class Item(Base):
    __tablename__ = 'item'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
                'name': self.name,
                'description': self.description,
                'id': self.id,
                }

engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)
