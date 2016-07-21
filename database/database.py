'''
Created on Jul 21, 2016

@author: carl
'''
import psycopg2

conn = psycopg2.connect("dbname=postgres user=carl")
cur = conn.cursor()

def get_intent_expressions(pipeline=None, training_data=None):