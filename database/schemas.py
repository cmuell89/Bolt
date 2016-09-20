'''
Created on Sep 19, 2016

@author: carl
'''

from sqlalchemy.ext.delcarative import declarative_base
from sqlalchemy import Column, Integer, String


Base = declarative_base()

class Expressions(Base):
    __tablename__ = 'expressions'
    id = Column(Integer, primary_key=True)
    expressions = Column(Text)
    intent_id = Column(Integer)
    
class Intents(Base):
    __tablename__ = 'intents'
    id = Column(Integer, primary_key=True)
    intents = Column(Text)
