'''
Created on Jul 21, 2016

@author: carl
'''
import psycopg2


class NLP_Database:
    def __init__(self, properties=None):
        if properties:
            # unsure if this will work
            self.conn = psycopg2.connect(properties)
        else:
            self.conn = psycopg2.connect(database="postgres", user="carl", password="007", host='/var/run/postgresql')
        self.cur = self.conn.cursor()


    def get_intents(self):
        try:    
            self.cur.execute("SELECT nlp.intents.intents FROM nlp.intents;")
            return self.cur.fetchall()
        except Exception as e:
            print(e)

    def get_intent_expressions(self,intent):
        if intent:
            try:
                self.cur.execute("SELECT nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id WHERE nlp.intents.intents = %s;", (intent,))
                return self.cur.fetchall()
            except Exception as e:
                print(e)
        else:
            raise Exception("Method expects valid intent string as argument")
                
    
    def get_intents_and_expressions(self):
        try:
            self.cur.execute("SELECT nlp.intents.intents, nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id;")
            return self.cur.fetchall()
        except Exception as e:
            print(e)
    
    def add_intent(self, intent):
        try:
            self.cur.execute("INSERT INTO nlp.intents (intents) VALUES (%s);", (intent,))
            return self.get_intents()
        except Exception as e:
            print(e)
    
    def add_expressions_to_intent(self, intent, expressions):
        if intent:
            try:
                self.cur.execute("SELECT nlp.intents.id FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
                intentID = self.cur.fetchone()
                if len(expressions) > 0:
                    for expression in expressions:
                        self.cur.execute("INSERT INTO nlp.expressions (expressions, intent_id) VALUES (%s, %s)", (expression, intentID))
                    return self.get_intent_expressions(intent)
                else:
                    raise Exception("Method expects a non-empty list of  expressions")
            except Exception as e:
                print(e)
        else:
            raise Exception("Method expects valid intent string as argument")   
            
    def delete_intent(self, intent):
        try:
            self.cur.execute("DELETE FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
            return self.get_intents()
        except Exception as e:
            print(e)
    
    def delete_all_intent_expressions(self, intent):
        try:
            self.cur.execute("DELETE FROM nlp.expressions WHERE nlp.expressions.intent_id = (SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s);", (intent,))
            return self.get_intents_and_expressions()
        except Exception as e:
            print(e)

        
    def close_database_connection(self):
        self.cur.close()
        self.conn.close()