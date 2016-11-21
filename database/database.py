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
from psycopg2.pool import ThreadedConnectionPool

logger = logging.getLogger('BOLT.db')

if os.environ.get('ENVIRONMENT') == 'prod':
    """ Connect to production database if in prod mode. """
    logger.debug('Created threaded database connection pool for PRODUCTION environment.')
    pool = ThreadedConnectionPool(2,
                                  20,
                                  database=os.environ.get('BOLT_DB_NAME'),
                                  user=os.environ.get('BOLT_DB_USERNAME'),
                                  password=os.environ.get('BOLT_DB_PASSWORD'),
                                  host=os.environ.get('BOLT_DB_HOSTNAME'),
                                  port=os.environ.get('BOLT_DB_PORT'))
else:
    """ Connect to local database if in test or dev mode. """
    logger.debug('Created threaded database conenction pool for TEST/DEV environment.')
    pool = ThreadedConnectionPool(2,
                                  20,
                                  database=os.environ.get('LOCAL_DB_NAME'),
                                  user=os.environ.get('LOCAL_DB_USER'),
                                  password=os.environ.get('LOCAL_DB_PASSWORD'),
                                  host=os.environ.get('LOCAL_DB_HOST'),
                                  port=os.environ.get('LOCAL_DB_PORT'))


class CoreDatabase:
    def __init__(self):
        try:
            logger.debug("Retrieiving database connection from pool.")
            self.conn = pool.getconn()
            self.cur = self.conn.cursor()
        except psycopg2.Error as e:
                raise e

    def release_database_connection(self):
        """
        Closes the cursor and releases the current database connection back to the pull
        """
        self.cur.close()
        pool.putconn(self.conn)
        logger.debug("Database connection released.")


class ExternalDatabaseEngine(CoreDatabase):
    """
    CoreDatabase extendning class that manages information retreival from materialized view of Shopify data.
    """
    def __init__(self):
        CoreDatabase.__init__(self)

    def get_keys(self):
        """
        Retrieves a list of database keys that with a one-to-one relationship with the bots stored in the database.
        :return: list of keys from database
        """
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
        """
        Retrieves a list of unique product names from database for the give key.
        :param key: key used to filter database results
        :return: list of product name entities
        """
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
        """
        Retrieves a list of unique product types from database for the give key.
        :param key: key used to filter database results
        :return: list of product type entities
        """
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
        """
        Retrieves a list of unique vendors from database for the give key.
        :param key: key used to filter database results
        :return: list of vendor entities
        """
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
    """
    Core Database extended class to manage intents and associate data
    """
    def __init__(self):
        CoreDatabase.__init__(self)

    def get_intents(self):
        """
        Gets a list of intents store in the database.
        :return: list of intents
        """
        try:
            self.cur.execute("SELECT intents FROM nlp.intents;")
            logger.debug("Retrieving all intents")
            list_of_intents = [x[0] for x in self.cur.fetchall()]
            return list_of_intents
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def add_intent(self, intent):
        """
        Adds an intent to the database
        :param intent: name of intent
        :return: updated list of intents
        """
        try:
            self.cur.execute("INSERT INTO nlp.intents (intents) VALUES (%s);", (intent,))
            self.conn.commit()
            logger.debug("Adding intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def delete_intent(self, intent):
        """
        Deletes intent from database
        :param intent: name of intent
        :return: updated list of intents via get_intents() method call
        """
        try:
            self.cur.execute("DELETE FROM nlp.expressions "
                             "WHERE nlp.expressions.intent_id = "
                             "(SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s);", (intent,))
            self.cur.execute("DELETE FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            self.conn.commit()
            logger.debug("Deleting intent: %s", intent)
            return self.get_intents()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def confirm_intent_exists(self, intent):
        """
        Confirm that an intent exists in the database
        :param intent: name of intent
        :return: True if exists; else false
        """
        try:
            self.cur.execute("SELECT intents "
                             "FROM nlp.intents "
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

    def get_intent_stopwords_and_entities(self, intent):
        """
        Retrives a list of stopwords for the given intent
        :param intent: name of intent
        :return: list of stopwords
        """
        # TODO NEEDS TEST!!!
        try:
            self.cur.execute("SELECT id FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT intents, stopwords, entities "
                                 "FROM nlp.intents "
                                 "WHERE nlp.intents.intents = %s;", (intent,))
                logger.debug("Retrieving intents and stopwords for the intent: %s", intent)
                intents_and_stopwords = self.cur.fetchall()
                return intents_and_stopwords
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)

    def get_intent_stopwords(self, intent):
        """
        Retrives a list of stopwords for the given intent
        :param intent: name of intent
        :return: list of stopwords
        """
        try:
            self.cur.execute("SELECT id FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT intents, stopwords "
                                 "FROM nlp.intents "
                                 "WHERE nlp.intents.intents = %s;", (intent,))
                logger.debug("Retrieving stopwords for the intent: %s", intent)
                intent_stopwords = self.cur.fetchall()
                return intent_stopwords
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)

    def add_stopwords_to_intent(self, intent, stopwords):
        """
        Adds stopwords to an intent
        :param intent: name of intent
        :param stopwords: list stopwords or single stopword string
        :return: list of intent stopwords
        """
        try:
            self.cur.execute("SELECT id "
                             "FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                if not isinstance(stopwords, list):
                    stopwords = [stopwords]
                if len(stopwords) > 0:
                    if isinstance(stopwords, list):
                        self.cur.execute("UPDATE nlp.intents "
                                         "SET stopwords = array_cat(nlp.intents.stopwords, %s) "
                                         "WHERE nlp.intents.id = %s", (stopwords, intent_id,))
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
        """
        Deletes stopwords from intent.
        :param intent: name of intent
        :param stopwords: list of words to remove from stopwords list
        :return: updated stopwords list for intent
        """
        try:
            existing_stopwords = self.get_intent_stopwords(intent)[0][1]
            if not isinstance(stopwords, list):
                stopwords = [stopwords]
            if len(stopwords) > 0:
                for stopword in stopwords:
                    if stopword in existing_stopwords:
                        existing_stopwords.remove(stopword)
                self.cur.execute("UPDATE nlp.intents "
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
        """
        Gets the entities for the given intent
        :param intent: name of intent
        :return: list of entities
        """
        try:
            self.cur.execute("SELECT id "
                             "FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT intents, entities "
                                 "FROM nlp.intents "
                                 "WHERE nlp.intents.intents = %s;", (intent,))
                logger.debug("Retrieving entity types for the intent: %s", intent)
                intent_entities = self.cur.fetchall()
                return intent_entities
            except psycopg2.Error as e:
                self.conn.rollback()
                logger.exception(e.pgerror)
                raise DatabaseError(e.pgerror)

    def add_entities_to_intent(self, intent, entities):
        """
        Adds a entities to an intent
        :param intent: name of intent
        :param entities: list of entities or single string entity
        :return: list of updated entities
        """
        try:
            self.cur.execute("SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
            raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                if not isinstance(entities, list):
                    entities = [entities]
                if len(entities) > 0:
                    logger.debug("Adding entities to intent: %s", intent)
                    self.cur.execute("UPDATE nlp.intents "
                                     "SET entities = array_cat(nlp.intents.entities, %s) "
                                     "WHERE nlp.intents.id = %s", (entities, intent_id,))
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
                self.cur.execute("UPDATE nlp.intents "
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
    Core database communication layer to manage Expressions in database.
    """
    def __init__(self):
        CoreDatabase.__init__(self)
        
    """
    Retrieval operations.
    """
    def get_intent_expressions(self, intent):
        """
        Gets expressiosn for given intent
        :param intent: name of intent
        :return: list of expressions
        """
        try: 
            self.cur.execute("SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s;", (intent,))
            intent_id = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intent_id is not None:
            try:
                self.cur.execute("SELECT expressions "
                                 "FROM nlp.intents "
                                 "INNER JOIN nlp.expressions "
                                 "ON nlp.intents.id = nlp.expressions.intent_id "
                                 "WHERE nlp.intents.intents = %s;", (intent,))
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
        """
        Gets all intents and the associated expressions
        :return: list of tuples (intent, expression)
        """
        try:
            self.cur.execute("SELECT intents, expressions "
                             "FROM nlp.intents "
                             "INNER JOIN nlp.expressions "
                             "ON nlp.intents.id = nlp.expressions.intent_id;")
            logger.debug("Retrieving all intents and expressions.")
            intents_and_expressions = list(map(lambda x: (x[0], x[1]), self.cur.fetchall()))
            return intents_and_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
        
    def get_unlabeled_expressions(self):
        """
        Retrieves all unlabeled expressions
        :return: list of unlabeled expressions
        """
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM nlp.unlabeled_expressions")
            logger.debug("Retrieving all unlabeled expressions.")
            unlabeled_expressions = list(map(lambda x: (x[0], x[1], x[2], x[3]), self.cur.fetchall()))
            return unlabeled_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def get_unlabeled_expression_by_id(self, id):
        """
        Gets the unlabeled expression by id.
        :param id: primary key id
        :return: returns the unlabeled expression if found or None if not found
        """
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM nlp.unlabeled_expressions "
                             "WHERE id = %s", (id,))
            logger.debug("Retrieving unlabeled expression by id.")
            unlabeled_expression = (lambda x: (x[0], x[1], x[2], x[3]))(self.cur.fetchone())
            return unlabeled_expression
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def get_archived_expressions(self):
        """
        Gets all archived expressions
        :return: list of archived expressions
        """
        try:
            self.cur.execute("SELECT id, expressions, estimated_intent, estimated_confidence "
                             "FROM nlp.archived_expressions")
            logger.debug("Retrieving all archived expressions.")
            archived_expressions = list(map(lambda x: (x[0], x[1], x[2], x[3]), self.cur.fetchall()))
            return archived_expressions
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    """
    Addition operations
    """
    def add_expressions_to_intent(self, intent, expressions):
        """
        Add expresssions to the given intent if it exists.
        :param intent: name of intent
        :param expressions: list of expressions or single string expression
        :return: returns list of the updates expressions for the intent
        """
        try: 
            self.cur.execute("SELECT id FROM nlp.intents "
                             "WHERE nlp.intents.intents = %s;", (intent,))
            intentID = self.cur.fetchone()
        except psycopg2.Error as e:
                raise DatabaseError(e.pgerror)
        if intentID is not None:
            try:
                if len(expressions) > 0:
                    logger.debug("Adding expressions to intent: %s", intent)
                    if isinstance(expressions, str):
                        # expressions is actually a singular string argument.
                        self.cur.execute("INSERT INTO nlp.expressions (expressions, intent_id) "
                                         "VALUES (%s, %s)", (expressions, intentID))
                    else:
                        for expression in expressions:
                            self.cur.execute("INSERT INTO nlp.expressions (expressions, intent_id) "
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
    
    def add_unlabeled_expression(self, expression, estimated_intent=None, estimated_confidence=None):
        """
        Add unalebeled expression to database
        :param expression: expression to add
        :param estimated_intent: the estimated intent by the classifier
        :param estimated_confidence: the estmiated confidence of the classifier
        :return: List of unlabeled expressions.
        """
        if expression:
            try:
                if len(expression) > 0:
                    logger.debug("Adding unlabeled expression to database.")
                    self.cur.execute("INSERT INTO nlp.unlabeled_expressions (expressions, estimated_intent, estimated_confidence) "
                                     "VALUES (%s, %s, %s)", (expression, estimated_intent, estimated_confidence))
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

    def add_archived_expression(self, expression, estimated_intent=None, estimated_confidence=None):
        """
        Add archived expression to database
        :param expression: expression to add
        :param estimated_intent: the estimated intent by the classifier
        :param estimated_confidence: the estmiated confidence of the classifier
        :return: List of archived expressions.
        """
        if expression:
            try:
                if len(expression) > 0:
                    logger.debug("Adding archived expression to database.")
                    self.cur.execute("INSERT INTO nlp.archived_expressions (expressions, estimated_intent, estimated_confidence) "
                                     "VALUES (%s, %s, %s)", (expression, estimated_intent, estimated_confidence))
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
        """
        Delete all expressiosn from an intent
        :param intent: intent name
        :type intent:
        :return: Empty list
        """
        try:
            self.cur.execute("DELETE FROM nlp.expressions "
                             "WHERE nlp.expressions.intent_id = "
                             "(SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s);", (intent,))
            self.conn.commit()
            logger.debug("Deleting all expressions from intent: %s", intent)
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)

    def delete_expressions_from_intent(self, intent, expressions):
        """
        Delete expressions from an intent
        :param intent: intent name
        :param expressions: list of expressions to be deleted
        :return: updated lsit of expressions for intent
        """
        try:
            for expression in expressions:
                self.cur.execute("DELETE FROM expressions "
                                 "WHERE nlp.expressions.intent_id = "
                                 "(SELECT id FROM nlp.intents WHERE nlp.intents.intents = %s) "
                                 "AND nlp.expressions.expressions = %s;", (intent, expression))
                logger.debug("Deleting the expression: '%s' from intent: %s", expression, intent)
                self.conn.commit()
            return self.get_intent_expressions(intent)
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_unlabeled_expression_by_id(self, id_):
        """
        Delete unlabeled expression by primary key id.
        :param id_: primary key id
        :return: Updated list of unlabeled expressions
        """
        try:
            self.cur.execute("DELETE FROM unlabeled_expressions "
                             "WHERE nlp.unlabeled_expressions.id = %s", (id_,))
            self.conn.commit()
            logger.debug("Deleting unlabeled expression.")
            return self.get_unlabeled_expressions()
        except psycopg2.Error as e:
            self.conn.rollback()
            logger.exception(e.pgerror)
            raise DatabaseError(e.pgerror)
    
    def delete_archived_expression_by_id(self, id_):
        """
        Delete archived expression by primary key id.
        :param id_: primary key id
        :return: Updated list of archived expressions
        """
        try:
            self.cur.execute("DELETE FROM archived_expressions "
                             "WHERE nlp.archived_expressions.id = %s", (id_,))
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
        """
        Confirm that archived expression exists for given id.
        :param id_: primary key id
        :return: True if exists; else false
        """
        try:
            self.cur.execute("SELECT id "
                             "FROM nlp.archived_expressions "
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
        """
        Confirm that unlabeled expression exists for given id.
        :param id_: primary key id
        :return: True if exists; else false
        """
        try:
            self.cur.execute("SELECT id "
                             "FROM nlp.unlabeled_expressions "
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

