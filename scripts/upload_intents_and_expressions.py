'''
Created on Sep 2, 2016

@author: carl
'''
import psycopg2
from utils import io

# Use environment variables and move such usage into production database module
conn = psycopg2.connect(database="see heroku", user="see heroku", password="see heroku", host='see heroku')
cur = conn.cursor()

training_set, training_labels = io.create_data_for_pipeline_from_file('../resources/intents.json')

labels = io.get_intents_from_JSON_data('../resources/intents.json')

for idx,val in enumerate(labels):
    cur.execute("INSERT INTO intents (intent) VALUES (%s)", (val,))
    

for idx, val in enumerate(training_labels):
    cur.execute("SELECT * FROM intents WHERE (intent = %s)",(val,))
    intent_id = cur.fetchone()[0]
    print(intent_id, training_set[idx])
    cur.execute("INSERT INTO expressions (expressions, intent_id) VALUES (%s, %s)",(training_set[idx], intent_id,))

conn.commit()

cur.close()
conn.close()