'''
Created on Jul 21, 2016

@author: Carl Mueller

Class: NLP_Database
Database layer communicating with postgreSQL via psycopg2 that manages expressions and intents for the classifier.

'''
import psycopg2
import logging
import os
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.db')

class NLP_Database:
    '''
    Core database communication layer to interact with postgreSQL. 
    Constructing an NLP_Databse depends on two sets of environment variables LOCAL vs RDS. 
    '''
    def __init__(self):
        try:
            if os.environ.get('ENVIRONMENT') is 'prod':
                self.conn = psycopg2.connect(database=os.environ.get('RDS_DB_NAME'), user=os.environ.get('RDS_USERNAME'), password=os.environ.get('RDS_PASSWORD'), host=os.environ.get('RDS_HOSTNAME'), port=os.environ.get('RDS_PORT')) 
            else:
                self.conn = psycopg2.connect(database=os.environ.get('LOCAL_DB_NAME'), user=os.environ.get('LOCAL_DB_USER'), password=os.environ.get('LOCAL_DB_PASSWORD'), host=os.environ.get('LOCAL_DB_HOST'), port=os.environ.get('LOCAL_DB_PORT'))
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            raise e

    def get_intents(self):
        try:
            self.cur.execute("SELECT public.intents.intents FROM public.intents;")
            logger.debug("Retrieving all intents")
            return self.cur.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_intent_expressions(self,intent):
        if intent:
            try:
                self.cur.execute("SELECT public.expressions.expressions FROM public.intents INNER JOIN public.expressions ON public.intents.id = public.expressions.intent_id WHERE public.intents.intents = %s;", (intent,))
                logger.debug("Retrieving all expressions for the intent: %s", intent)
                return self.cur.fetchall()
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid intent string as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
                
    
    def get_intents_and_expressions(self):
        try:
            self.cur.execute("SELECT public.intents.intents, public.expressions.expressions FROM public.intents INNER JOIN public.expressions ON public.intents.id = public.expressions.intent_id;")
            logger.debug("Retrieving all intents and expressions.")
            return self.cur.fetchall()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def add_intent(self, intent):
        try:
            self.cur.execute("INSERT INTO public.intents (intents) VALUES (%s);", (intent,))
            self.conn.commit()
            logger.debug("Adding intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def add_expressions_to_intent(self, intent, expressions):
        if intent:
            try:
                self.cur.execute("SELECT public.intents.id FROM public.intents WHERE public.intents.intents = %s;", (intent,))
                intentID = self.cur.fetchone()
                if len(expressions) > 0:
                    for expression in expressions:
                        self.cur.execute("INSERT INTO public.expressions (expressions, intent_id) VALUES (%s, %s)", (expression, intentID))
                        self.conn.commit()
                    logger.debug("Adding expressions to intent: %s", intent)
                    return self.get_intent_expressions(intent)
                else:
                    msg = "Method expects a non-empty list of expressions"
                    logger.exception(msg)
                    raise DatabaseInputError(msg)
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid intent string as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
            
    def delete_intent(self, intent):
        try:
            self.delete_all_intent_expressions(intent)
            self.cur.execute("DELETE FROM public.intents WHERE public.intents.intents = %s;", (intent,))
            self.conn.commit()
            logger.debug("Deleting intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_all_intent_expressions(self, intent):
        try:
            print(intent)
            self.cur.execute("DELETE FROM public.expressions WHERE public.expressions.intent_id = (SELECT id FROM public.intents WHERE public.intents.intents = %s);", (intent,))
            self.conn.commit()
            logger.debug("Deleting all expressions from intent: %s", intent)
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_expressions_from_intent(self, intent, expressions):
        try:
            for expression in expressions:
                self.cur.execute("DELETE FROM public.expressions WHERE public.expressions.intent_id = (SELECT id FROM public.intents WHERE public.intents.intents = %s) AND public.expressions.expressions = %s;", (intent, expression))
                logger.debug("Deleting the expression: '%s' from intent: %s", expression, intent)
                self.conn.commit()
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

        
    def close_database_connection(self):
        self.cur.close()
        self.conn.close()