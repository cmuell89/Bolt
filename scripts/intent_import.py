'''
Created on Jul 21, 2016

@author: carl
'''
import psycopg2
from utils import io

conn = psycopg2.connect(database="postgres", user="carl", password="007", host='/var/run/postgresql')
cur = conn.cursor()

training_set, training_labels = io.create_data_for_pipeline_from_file('../resources/intents.json')

labels = io.get_intents_from_JSON_data('../resources/intents.json')

for idx,val in enumerate(labels):
    cur.execute("INSERT INTO nlp.intents (intents) VALUES (%s)", (val,))
    

for idx, val in enumerate(training_labels):
    cur.execute("SELECT * FROM nlp.intents WHERE (intents = %s)",(val,))
    intent_id = cur.fetchone()[0]
    print(intent_id, training_set[idx])
    cur.execute("INSERT INTO nlp.expressions (expressions, intent_id) VALUES (%s, %s)",(training_set[idx], intent_id,))

conn.commit()

cur.close()
conn.close()