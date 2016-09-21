'''
Created on Sep 19, 2016

@author: carl
'''

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Text, ForeignKey


Base = declarative_base()

class Expressions(Base):
    __tablename__ = 'expressions'
    id = Column(Integer, primary_key=True, unique=True)
    expressions = Column(Text)
    intent_id = Column(Integer, ForeignKey("intents.id"))
    
class Intents(Base):
    __tablename__ = 'intents'
    id = Column(Integer, primary_key=True, unique=True)
    intents = Column(Text)
