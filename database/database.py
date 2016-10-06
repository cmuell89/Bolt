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

class NLPDatabase:
    '''
    Core database communication layer to interact with postgreSQL. 
    Constructing an NLP_Databse depends on two sets of environment variables LOCAL vs RDS. 
    '''
    def __init__(self):
        try:
            if os.environ.get('ENVIRONMENT')=='prod':
                self.conn = psycopg2.connect(database=os.environ.get('RDS_DB_NAME'), user=os.environ.get('RDS_USERNAME'), password=os.environ.get('RDS_PASSWORD'), host=os.environ.get('RDS_HOSTNAME'), port=os.environ.get('RDS_PORT')) 
            else:
                self.conn = psycopg2.connect(database=os.environ.get('LOCAL_DB_NAME'), user=os.environ.get('LOCAL_DB_USER'), password=os.environ.get('LOCAL_DB_PASSWORD'), host=os.environ.get('LOCAL_DB_HOST'), port=os.environ.get('LOCAL_DB_PORT'))
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            raise e
        
    '''
    Retrieval operations.
    '''
    def get_intents(self):
        try:
            self.cur.execute("SELECT intents FROM public.intents;")
            logger.debug("Retrieving all intents") 
            list_of_intents = list(map(lambda x: x[0], self.cur.fetchall()))          
            return list_of_intents 
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_intent_expressions(self,intent):
        try: 
            self.cur.execute("SELECT id FROM public.intents WHERE public.intents.intents = %s;", (intent,))
            intent_ID = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intent_ID is not None:
            try:
                self.cur.execute("SELECT expressions FROM public.intents INNER JOIN public.expressions ON public.intents.id = public.expressions.intent_id WHERE public.intents.intents = %s;", (intent,))
                logger.debug("Retrieving all expressions for the intent: %s", intent)
                list_of_expressions = list(map(lambda x: x[0], self.cur.fetchall()))
                return list_of_expressions
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid/existing intent as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
                
    
    def get_intents_and_expressions(self):
        try:
            self.cur.execute("SELECT intents, expressions FROM public.intents INNER JOIN public.expressions ON public.intents.id = public.expressions.intent_id;")
            logger.debug("Retrieving all intents and expressions.")
            intents_and_expressions = list(map(lambda x: (x[0], x[1]), self.cur.fetchall()))
            return intents_and_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
        
    def get_unlabeled_expressions(self):
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence FROM public.unlabeled_expressions")
            logger.debug("Retrieving all unlabeled expressions.")
            unlabeled_expressions = list(map(lambda x: (x[0], x[1], x[2], x[3]), self.cur.fetchall()))
            return unlabeled_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_unlabeled_expression_by_id(self, id):
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence FROM public.unlabeled_expressions WHERE id = %s", (id,))
            logger.debug("Retrieving unlabeled expression by id.")
            unlabeled_expression = (lambda x: (x[0], x[1], x[2], x[3]))(self.cur.fetchone())
            return unlabeled_expression
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    '''
    Addition operations
    '''
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
        try: 
            self.cur.execute("SELECT id FROM public.intents WHERE public.intents.intents = %s;", (intent,))
            intentID = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intentID is not None:
            try:
                if len(expressions) > 0:
                    logger.debug("Adding expressions to intent: %s", intent)
                    if isinstance(expressions, str):
                        # expressions is actually a singular string argument.
                        self.cur.execute("INSERT INTO public.expressions (expressions, intent_id) VALUES (%s, %s)", (expressions, intentID))
                    else:
                        for expression in expressions:
                            self.cur.execute("INSERT INTO public.expressions (expressions, intent_id) VALUES (%s, %s)", (expression, intentID))
                    self.conn.commit()
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
            msg = "Method expects valid/existing intent as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
    
    def add_unlabeled_expression(self, expression, estimatedIntent=None, estimatedConfidence=None):
        if expression:
            try:
                if len(expression) > 0:
                    logger.debug("Adding unlabeled expression to database.")
                    self.cur.execute("INSERT INTO public.unlabeled_expressions (expressions, estimated_intent, estimated_confidence) VALUES (%s, %s, %s)", (expression, estimatedIntent, estimatedConfidence))
                    self.conn.commit()
                    return self.get_unlabeled_expressions()
                else:
                    msg = "Method expects an unlabeled expression of length > 0."
                    logger.exception(msg)
                    raise DatabaseInputError(msg)
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError
        else:
            msg = "Method expects valid expression string as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
    '''
    Untested
    '''
    def add_archived_expression(self, expression, estimatedIntent=None, estimatedConfidence=None):
        if expression:
            try:
                if len(expression) > 0:
                    logger.debug("Adding archived expression to database.")
                    self.cur.execute("INSERT INTO public.archived_expressions (expressions, estimated_intent, estimated_confidence) VALUES (%s, %s, %s)", (expression, estimatedIntent, estimatedConfidence))
                    self.conn.commit()
                    return self.get_unlabeled_expressions()
                else:
                    msg = "Method expects an archived expression of length > 0."
                    logger.exception(msg)
                    raise DatabaseInputError(msg)
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError
        else:
            msg = "Method expects valid expression string as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)
    '''
    Deletion operations
    ''' 
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
            self.cur.execute("DELETE FROM expressions WHERE public.expressions.intent_id = (SELECT id FROM public.intents WHERE public.intents.intents = %s);", (intent,))
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
                self.cur.execute("DELETE FROM expressions WHERE public.expressions.intent_id = (SELECT id FROM public.intents WHERE public.intents.intents = %s) AND public.expressions.expressions = %s;", (intent, expression))
                logger.debug("Deleting the expression: '%s' from intent: %s", expression, intent)
                self.conn.commit()
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_unlabeled_expression(self, id):
        try:
            self.cur.execute("DELETE FROM unlabeled_expressions WHERE public.unlabeled_expressions.id = %s", (id,))
            self.conn.commit()
            logger.debug("Deleting unlabeled expression.")
            return self.get_unlabeled_expressions()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    '''
    Confirmation operations
    '''
    def confirm_intent_exists(self, intent):
        try:
            self.cur.execute("SELECT intents FROM public.intents WHERE intents = (%s)", (intent,))
            logger.debug("Confirming intent exists") 
            result = self.cur.fetchone()
            if result is None:
                return False
            else:
                return True          
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
        
    def close_database_connection(self):
        self.cur.close()
        self.conn.close()