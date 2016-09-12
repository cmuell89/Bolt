'''
Created on Jul 21, 2016

@author: carl
'''
import psycopg2
import logging
import os

class NLP_Database:
    def __init__(self):
        if 'RDS_HOSTNAME' in os.environ:
            self.conn = psycopg2.connect(database=os.environ.get('RDS_DB_NAME'), user=os.environ.get('RDS_USERNAME'), password=os.environ.get('RDS_PASSWORD'), host=os.environ.get('RDS_HOSTNAME'), port=os.environ.get('RDS_PORT'))
        else:
            self.conn = psycopg2.connect(database=os.environ.get('PGSQL_DB_NAME'), user=os.environ.get('PGSQL_DB_USER'), password=os.environ.get('PGSQL_DB_PASSWORD'), host=os.environ.get('PGSQL_DB_HOST'), port=os.environ.get('PGSQL_DB_PORT'))
        self.cur = self.conn.cursor()
        self.logger = logging.getLogger('bolt.nlpDB')


    def get_intents(self):
        try:
            self.cur.execute("SELECT nlp.intents.intents FROM nlp.intents;")
            self.logger.info("Retrieving all intents")
            return self.cur.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)

    def get_intent_expressions(self,intent):
        if intent:
            try:
                self.cur.execute("SELECT nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id WHERE nlp.intents.intents = %s;", (intent,))
                self.logger.info("Retrieving all expressions for the intent: %s", intent)
                return self.cur.fetchall()
            except psycopg2.Error as e:
                self.conn.rollback()
                self.logger.exception(e.pgerror)
                raise Exception.DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid intent string as argument"
            logging.exception(msg)
            raise Exception.DatabaseInputError(msg)
                
    
    def get_intents_and_expressions(self):
        try:
            self.cur.execute("SELECT nlp.intents.intents, nlp.expressions.expressions FROM nlp.intents INNER JOIN nlp.expressions ON nlp.intents.id = nlp.expressions.intent_id;")
            self.logger.info("Retrieving all intents and expressions.")
            return self.cur.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)
    
    def add_intent(self, intent):
        try:
            self.cur.execute("INSERT INTO nlp.intents (intents) VALUES (%s);", (intent,))
            self.conn.commit()
            self.logger.info("Adding intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)
    
    def add_expressions_to_intent(self, intent, expressions):
        if intent:
            try:
                self.cur.execute("SELECT nlp.intents.id FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
                intentID = self.cur.fetchone()
                if len(expressions) > 0:
                    for expression in expressions:
                        self.cur.execute("INSERT INTO nlp.expressions (expressions, intent_id) VALUES (%s, %s)", (expression, intentID))
                        self.conn.commit()
                    self.logger.info("Adding expressions to intent: %s", intent)
                    return self.get_intent_expressions(intent)
                else:
                    msg = "Method expects a non-empty list of expressions"
                    self.logger.exception(msg)
                    raise Exception.DatabaseInputError(msg)
            except psycopg2.Error as e:
                self.conn.rollback()
                self.logger.exception(e.pgerror)
                raise Exception.DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid intent string as argument"
            self.logger.exception(msg)
            raise e.DatabaseInputError(msg)
            
    def delete_intent(self, intent):
        try:
            self.delete_all_intent_expressions(intent)
            self.cur.execute("DELETE FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
            self.conn.commit()
            self.logger.info("Deleting intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)
    
    def delete_all_intent_expressions(self, intent):
        try:
            self.cur.execute("DELETE FROM nlp.expressions WHERE nlp.expressions.intent_id = (SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s);", (intent,))
            self.conn.commit()
            self.logger.info("Deleting all expressions from intent: %s", intent)
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)
    
    def delete_expressions_from_intent(self, intent, expressions):
        try:
            for expression in expressions:
                self.cur.execute("DELETE FROM nlp.expressions WHERE nlp.expressions.intent_id = (SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s) AND nlp.expressions.expressions = %s;", (intent, expression))
                self.logger.info("Deleting the expression: '%s' from intent: %s", expression, intent)
                self.conn.commit()
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            self.logger.exception(e.pgerror)
            raise Exception.DatabaseError(e.pgerror)

        
    def close_database_connection(self):
        self.cur.close()
        self.conn.close()