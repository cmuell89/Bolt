'''
Created on Jul 21, 2016

@author: carl
'''
import psycopg2


class NLP_Database:
    def __init__(self, properties=None):
        if properties:
            self.conn = psycopg2.connect(properties)
        else:
            self.conn = psycopg2.connect(database="postgres", user="carl", password="007", host='/var/run/postgresql')
        self.cur = self.conn.cursor()


    def get_intents(self):
        try:    
            self.cur.execute("SELECT nlp.intents.intents, nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id;")
            return self.cur.fetchall()
        except Exception as e:
            print(e)
            pass

    def get_intent_expressions(self,intent):
        if intent:
            try:
                self.cur.execute("SELECT intents FROM nlp.intents WHERE intents = intent")
                return self.cur.fetchall()
            except Exception as e:
                print(e)
                pass
        else:
            raise Exception('method expects valid intent string as argument')
                
    
    def get_intents_and_expressions(self):
        try:
            self.cur.execute("SELECT nlp.intents.intents, nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id;")
            return self.cur.fetchall()
        except Exception as e:
            print(e)
            pass
        
    def close_database_connection(self):
        self.cur.close()
        self.conn.close()