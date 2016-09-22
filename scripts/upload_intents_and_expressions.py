'''
Created on Sep 2, 2016

@author: carl
'''
import psycopg2
from utils import io
from os.path import join, dirname
from dotenv import load_dotenv
import csv
import os

if __name__ == '__main__':
    if os.path.isfile('../.env')==True:
            dotenv_path = join(dirname(__file__), '../.env')
            load_dotenv(dotenv_path)
        
    database = os.environ.get('LOCAL_DB_NAME') 
    user = os.environ.get('LOCAL_DB_USERNAME')
    password = os.environ.get('LOCAL_DB_PASSWORD')
    host = os.environ.get('LOCAL_DB_HOSTNAME')
    port = os.environ.get('LOCAL_DB_PORT')
    # Use environment variables and move such usage into production database module
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
    cur = conn.cursor()
    
    training_set, training_labels = io.create_data_for_pipeline_from_file('../resources/intents.json')
    
    labels = io.get_intents_from_JSON_data('../resources/intents.json')
    
    for idx,val in enumerate(labels):
        cur.execute("INSERT INTO intents (intents) VALUES (%s)", (val,))
        
    
    for idx, val in enumerate(training_labels):
        cur.execute("SELECT * FROM intents WHERE (intents = %s)",(val,))
        intent_id = cur.fetchone()[0]
        print(intent_id, training_set[idx])
        cur.execute("INSERT INTO expressions (expressions, intent_id) VALUES (%s, %s)",(training_set[idx], intent_id,))
    
    conn.commit()
    
    cur.close()
    conn.close()