from database.schemas import Base
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from os.path import join, dirname
from dotenv import load_dotenv
import os

"""
Database schemas are defined in database.schemas.py
"""

    
if __name__ == '__main__':
    
    if os.path.isfile('../.env')==True:
        dotenv_path = join(dirname(__file__), '../.env')
        load_dotenv(dotenv_path)
    
    database = os.environ.get('RDS_DB_NAME') 
    user = os.environ.get('RDS_USERNAME')
    password = os.environ.get('RDS_PASSWORD')
    host = os.environ.get('RDS_HOSTNAME')
    port = os.environ.get('RDS_PORT')
    
    connectionURL = URL('postgres', user, password, host, port, database)
    
    engine = create_engine(connectionURL, echo=True)

    Base.metadata.create_all(engine)