from database.schemas import Base, Expressions, Intents
from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL

if os.path.isfile('../env')==True:
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    
if __name__ == '__main__':
    
    database = os.environ.get('PGSQL_DB_NAME') 
    user = os.environ.get('PGSQL_DB_USER')
    password = os.environ.get('PGSQL_DB_PASSWORD')
    host = os.environ.get('PGSQL_DB_HOST')
    port = os.environ.get('PGSQL_DB_PORT')
    
    connectionURL = URL('psycopg2', user, password, host, port, database)
    
    engine = create_engine(connectionURL)
    
    Base.metadata.create_all(engine)