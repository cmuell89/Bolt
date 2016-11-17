"""
Created on Jul 21, 2016

@author: Carl Mueller

Class: NLPDatabase
Database layer communicating with postgreSQL via psycopg2 that manages expressions and intents for the classifier.

"""
import psycopg2
import logging
import os
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.db')


class CoreDatabase:
    def __init__(self, database='BOLT'):
        try:
            if database == 'BOLT':
                self.conn = psycopg2.connect(database=os.environ.get('BOLT_DB_NAME'),
                                             user=os.environ.get('BOLT_DB_USERNAME'),
                                             password=os.environ.get('BOLT_DB_PASSWORD'),
                                             host=os.environ.get('BOLT_DB_HOSTNAME'),
                                             port=os.environ.get('BOLT_DB_PORT'))
            elif database == 'SHOPIFY':
                self.conn = psycopg2.connect(database=os.environ.get('SHOPIFY_DB_NAME'),
                                             user=os.environ.get('SHOPIFY_DB_USERNAME'),
                                             password=os.environ.get('SHOPIFY_DB_PASSWORD'),
                                             host=os.environ.get('SHOPIFY_DB_HOSTNAME'),
                                             port=os.environ.get('SHOPIFY_DB_PORT'))
            elif database == 'LOCAL':
                self.conn = psycopg2.connect(database=os.environ.get('LOCAL_DB_NAME'),
                                             user=os.environ.get('LOCAL_DB_USER'),
                                             password=os.environ.get('LOCAL_DB_PASSWORD'),
                                             host=os.environ.get('LOCAL_DB_HOST'),
                                             port=os.environ.get('LOCAL_DB_PORT'))
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
            raise e

    def close_database_connection(self):
        self.cur.close()
        self.conn.close()


class ExternalDatabaseEngine(CoreDatabase):
    def __init__(self):
        CoreDatabase.__init__(self, 'SHOPIFY')

    def get_keys(self):
        try:
            self.cur.execute("SELECT DISTINCT ON (key) key "
                             "FROM public.entities")
            logger.debug("Retrieving keys from shopify database")
            list_of_keys = [x[0] for x in self.cur.fetchall()]
            return list_of_keys
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_product_names_by_key(self, key):
        try:
            self.cur.execute("SELECT DISTINCT ON (product_name) product_name "
                             "FROM public.entities "
                             "WHERE key = %s", (key,))
            logger.debug("Retrieving product name entities from shopify database for given key.")
            product_name_entities = [x[0] for x in self.cur.fetchall()]
            return product_name_entities
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_product_types_by_key(self, key):
        try:
            self.cur.execute("SELECT DISTINCT ON (product_type) product_type "
                             "FROM public.entities "
                             "WHERE key = %s", (key,))
            logger.debug("Retrieving product type entities from shopify database for given key.")
            product_name_entities = [x[0] for x in self.cur.fetchall()]
            return product_name_entities
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_vendors_by_key(self, key):
        try:
            self.cur.execute("SELECT DISTINCT ON (vendor) vendor "
                             "FROM public.entities "
                             "WHERE key = %s", (key,))
            logger.debug("Retrieving vendor entities from shopify database for given key.")
            vendor_entities = [x[0] for x in self.cur.fetchall()]
            return vendor_entities
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    # TODO: get_options_by_key()


class IntentsDatabaseEngine(CoreDatabase):
    def __init__(self):
        if os.environ.get('ENVIRONMENT') == 'prod':
            database = 'BOLT'
        else:
            database = 'LOCAL'
        CoreDatabase.__init__(self, database)

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

    def delete_intent(self, intent):
        try:
            self.cur.execute("DELETE FROM public.expressions "
                             "WHERE public.expressions.intent_id = "
                             "(SELECT id FROM public.intents WHERE public.intents.intents = %s);", (intent,))
            self.cur.execute("DELETE FROM public.intents "
                             "WHERE public.intents.intents = %s;", (intent,))
            self.conn.commit()
            logger.debug("Deleting intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def confirm_intent_exists(self, intent):
        try:
            self.cur.execute("SELECT intents "
                             "FROM public.intents "
                             "WHERE intents = (%s)", (intent,))
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

    def get_intent_stopwords(self, intent):
        try:
            self.cur.execute("SELECT id FROM public.intents "
                             "WHERE public.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT intents, stopwords "
                                 "FROM public.intents "
                                 "WHERE public.intents.intents = %s;", (intent,))
                logger.debug("Retrieving stopwords for the intent: %s", intent)
                intent_stopwords = self.cur.fetchall()
                return intent_stopwords
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)

    def add_stopwords_to_intent(self, intent, stopwords):
        try:
            self.cur.execute("SELECT id "
                             "FROM public.intents "
                             "WHERE public.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                if not isinstance(stopwords, list):
                    stopwords = [stopwords]
                if len(stopwords) > 0:
                    if isinstance(stopwords, list):
                        self.cur.execute("UPDATE public.intents "
                                         "SET stopwords = array_cat(public.intents.stopwords, %s) "
                                         "WHERE public.intents.id = %s", (stopwords, intent_id,))
                        self.conn.commit()
                        return self.get_intent_stopwords(intent)
                else:
                    msg = "Method expects a string or non-empty list of stopwords"
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

    def delete_stopwords_from_intent(self, intent, stopwords):
        try:
            existing_stopwords = self.get_intent_stopwords(intent)[0][1]
            if not isinstance(stopwords, list):
                stopwords = [stopwords]
            if len(stopwords) > 0:
                for stopword in stopwords:
                    if stopword in existing_stopwords:
                        existing_stopwords.remove(stopword)
                self.cur.execute("UPDATE public.intents "
                                 "SET stopwords = %s "
                                 "WHERE intents.intents = %s", (existing_stopwords, intent))
                self.conn.commit()
                return self.get_intent_stopwords(intent)
            else:
                msg = "Method expects a non-null string or non-empty list of stopwords"
                logger.exception(msg)
                raise DatabaseInputError(msg)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_intent_entities(self, intent):
        try:
            self.cur.execute("SELECT id "
                             "FROM public.intents "
                             "WHERE public.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT intents, entities "
                                 "FROM public.intents "
                                 "WHERE public.intents.intents = %s;", (intent,))
                logger.debug("Retrieving entity types for the intent: %s", intent)
                intent_entities = self.cur.fetchall()
                return intent_entities
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)

    def add_entities_to_intent(self, intent, entities):
        try:
            self.cur.execute("SELECT id FROM public.intents WHERE public.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                if not isinstance(entities, list):
                    entities = [entities]
                if len(entities) > 0:
                    logger.debug("Adding entities to intent: %s", intent)
                    self.cur.execute("UPDATE public.intents "
                                     "SET entities = array_cat(public.intents.entities, %s) "
                                     "WHERE public.intents.id = %s", (entities, intent_id,))
                    self.conn.commit()
                    return self.get_intent_entities(intent)
                else:
                    msg = "Method expects a string or non-empty list of entities"
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

    def delete_entities_from_intent(self, intent, entities):
        try:
            exisiting_entities = self.get_intent_entities(intent)[0][1]
            if not isinstance(entities, list):
                entities = [entities]
            if len(entities) > 0:
                for entity in entities:
                    if entity in exisiting_entities:
                        exisiting_entities.remove(entity)
                self.cur.execute("UPDATE public.intents "
                                 "SET entities = %s "
                                 "WHERE intents.intents = %s", (exisiting_entities, intent))
                self.conn.commit()
                return self.get_intent_entities(intent)
            else:
                msg = "Method expects a non-null string or non-empty list of entities"
                logger.exception(msg)
                raise DatabaseInputError(msg)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)


class ExpressionsDatabaseEngine(CoreDatabase):
    """
    Core database communication layer to interact with postgreSQL to manage expresssions in Bolt.
    Constructing an NLP_Databse depends on two sets of environment variables LOCAL vs RDS. 
    """
    def __init__(self):
        if os.environ.get('ENVIRONMENT') == 'prod':
            database = 'BOLT'
        else:
            database = 'LOCAL'
        CoreDatabase.__init__(self, database)
        
    """
    Retrieval operations.
    """
    def get_intent_expressions(self, intent):
        try: 
            self.cur.execute("SELECT id FROM public.intents WHERE public.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT expressions "
                                 "FROM public.intents "
                                 "INNER JOIN public.expressions "
                                 "ON public.intents.id = public.expressions.intent_id "
                                 "WHERE public.intents.intents = %s;", (intent,))
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
            self.cur.execute("SELECT intents, expressions "
                             "FROM public.intents "
                             "INNER JOIN public.expressions "
                             "ON public.intents.id = public.expressions.intent_id;")
            logger.debug("Retrieving all intents and expressions.")
            intents_and_expressions = list(map(lambda x: (x[0], x[1]), self.cur.fetchall()))
            return intents_and_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
        
    def get_unlabeled_expressions(self):
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM public.unlabeled_expressions")
            logger.debug("Retrieving all unlabeled expressions.")
            unlabeled_expressions = list(map(lambda x: (x[0], x[1], x[2], x[3]), self.cur.fetchall()))
            return unlabeled_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_unlabeled_expression_by_id(self, id):
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM public.unlabeled_expressions "
                             "WHERE id = %s", (id,))
            logger.debug("Retrieving unlabeled expression by id.")
            unlabeled_expression = (lambda x: (x[0], x[1], x[2], x[3]))(self.cur.fetchone())
            return unlabeled_expression
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def get_archived_expressions(self):
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM public.archived_expressions")
            logger.debug("Retrieving all archived expressions.")
            unlabeled_expressions = list(map(lambda x: (x[0], x[1], x[2], x[3]), self.cur.fetchall()))
            return unlabeled_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    """
    Addition operations
    """
    def add_expressions_to_intent(self, intent, expressions):
        try: 
            self.cur.execute("SELECT id FROM public.intents "
                             "WHERE public.intents.intents = %s;", (intent,))
            intentID = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intentID is not None:
            try:
                if len(expressions) > 0:
                    logger.debug("Adding expressions to intent: %s", intent)
                    if isinstance(expressions, str):
                        # expressions is actually a singular string argument.
                        self.cur.execute("INSERT INTO public.expressions (expressions, intent_id) "
                                         "VALUES (%s, %s)", (expressions, intentID))
                    else:
                        for expression in expressions:
                            self.cur.execute("INSERT INTO public.expressions (expressions, intent_id) "
                                             "VALUES (%s, %s)", (expression, intentID))
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
                    self.cur.execute("INSERT INTO public.unlabeled_expressions (expressions, estimated_intent, estimated_confidence) "
                                     "VALUES (%s, %s, %s)", (expression, estimatedIntent, estimatedConfidence))
                    self.conn.commit()
                    return self.get_unlabeled_expressions()
                else:
                    msg = "Method expects an unlabeled expression of length > 0."
                    logger.exception(msg)
                    raise DatabaseInputError(msg)
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)
        else:
            msg = "Method expects valid expression string as argument"
            logger.exception(msg)
            raise DatabaseInputError(msg)

    def add_archived_expression(self, expression, estimatedIntent=None, estimatedConfidence=None):
        if expression:
            try:
                if len(expression) > 0:
                    logger.debug("Adding archived expression to database.")
                    self.cur.execute("INSERT INTO public.archived_expressions (expressions, estimated_intent, estimated_confidence) "
                                     "VALUES (%s, %s, %s)", (expression, estimatedIntent, estimatedConfidence))
                    self.conn.commit()
                    return self.get_archived_expressions()
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
    """
    Deletion operations
    """
    def delete_all_intent_expressions(self, intent):
        try:
            self.cur.execute("DELETE FROM public.expressions "
                             "WHERE public.expressions.intent_id = "
                             "(SELECT id FROM public.intents WHERE public.intents.intents = %s);", (intent,))
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
                self.cur.execute("DELETE FROM expressions "
                                 "WHERE public.expressions.intent_id = "
                                 "(SELECT id FROM public.intents WHERE public.intents.intents = %s) "
                                 "AND public.expressions.expressions = %s;", (intent, expression))
                logger.debug("Deleting the expression: '%s' from intent: %s", expression, intent)
                self.conn.commit()
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_unlabeled_expression(self, id_):
        try:
            self.cur.execute("DELETE FROM unlabeled_expressions "
                             "WHERE public.unlabeled_expressions.id = %s", (id_,))
            self.conn.commit()
            logger.debug("Deleting unlabeled expression.")
            return self.get_unlabeled_expressions()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_archived_expression(self, id_):
        try:
            self.cur.execute("DELETE FROM archived_expressions "
                             "WHERE public.archived_expressions.id = %s", (id_,))
            self.conn.commit()
            logger.debug("Deleting archived expression.")
            return self.get_archived_expressions()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    """
    Confirmation operations
    """
    def confirm_archived_expression_exists(self, id_):
        try:
            self.cur.execute("SELECT id "
                             "FROM public.archived_expressions "
                             "WHERE id = (%s)", (id_,))
            logger.debug("Confirming archived expression exists") 
            result = self.cur.fetchone()
            if result is None:
                return False
            else:
                return True          
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def confirm_unlabeled_expression_exists(self, id_):
        try:
            self.cur.execute("SELECT id "
                             "FROM public.unlabeled_expressions "
                             "WHERE id = (%s)", (id_,))
            logger.debug("Confirming unlabeled expression exists") 
            result = self.cur.fetchone()
            if result is None:
                return False
            else:
                return True          
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

