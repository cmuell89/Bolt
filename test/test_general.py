'''
Created on Jul 21, 2016

@author: Carl Mueller

Unit tests for general Bolt module functions, classes and methods. 
'''
import unittest
import sklearn
import settings
import logging
from utils.custom_assertions import CustomAssertions
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor, Classifier
from nlp.ner.gazetteer import GazetteerModelBuilder, GazetteerModelAccessor, Gazetteer
from database.database import EntitiesDatabase, StopwordsDatabase, ExpressionsDatabase, IntentsDatabase
from builtins import int, str

logger = logging.getLogger('BOLT.test')


class EntitiesDatabaseTest(unittest.TestCase, CustomAssertions):

    @classmethod
    def setUpClass(cls):
        logger.info("Testing for NLP_Database methods:")

    @classmethod
    def tearDownClass(cls):
        logger.info('')

    def test_intent_entities(self):
        self.fail()

    def test_add_entities_to_intent(self):
        self.fail()

    def test_delete_entities_from_intent(self):
        self.fail()


class StopwordsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
        Class for unit testing all methods with the database.database.NLP_Database class
        """

    @classmethod
    def setUpClass(cls):
        logger.info("Testing for NLP_Database methods:")

    @classmethod
    def tearDownClass(cls):
        logger.info('')

    def test_get_intent_stopwords(self):
        self.fail()

    def test_add_stopwords_to_intent(self):
        self.fail()

    def test_delete_stopwords_from_intent(self):
        self.fail()


class IntentsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
       Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(cls):
        logger.info("Testing for NLP_Database methods:")

    @classmethod
    def tearDownClass(cls):
        logger.info('')

    def test_get_intents(self):
        logger.debug("Testing for 'get_intents'")
        db = ExpressionsDatabase()
        intents = db.get_intents()
        self.assertListOfString(intents)
        db.close_database_connection()
        logger.info("Testing for 'get_intents' a success!")

    def test_add_intent(self):
        logger.debug("Testing for 'add_intent'")
        db = ExpressionsDatabase()
        new_list_of_intents = db.add_intent('some-new-intent')
        self.assertIn('some-new-intent', new_list_of_intents)
        db.delete_intent('some-new-intent')
        db.close_database_connection()
        logger.info("Testing for 'add_intent' a success!")

    def test_delete_intent(self):
        logger.debug("\nTesting for 'delete_intent'")
        db = IntentsDatabase()
        db.add_intent('soon-to-be-deleted')
        results = db.delete_intent('soon-to-be-deleted')
        self.assertNotIn(('soon-to-be-deleted',), results)
        logger.info("Testing for 'delete_intent' a success!")

    def test_confirm_intent_exists(self):
        logger.debug("\nTesting for 'confirm_intent_exists'")
        db = IntentsDatabase()
        db.add_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(True, intent_exists)
        db.delete_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(False, intent_exists)
        logger.info("Testing for 'confirm_intent_exists' a success!")


class ExpressionsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(cls):
        logger.info("Testing for NLP_Database methods:")

    @classmethod
    def tearDownClass(cls):
        logger.info('')
    
    '''
    Retrieval operations.
    '''
    def test_get_intents_and_expressions(self):
        logger.debug("Testing for 'get_intents_and_expressions'")
        db = ExpressionsDatabase()
        intents_and_expressions = db.get_intents_and_expressions()
        self.assertListOfTuples(intents_and_expressions, [str, str])
        db.close_database_connection()
        logger.info("Testing for 'get_intents_and_expressions' a success!")
    
    def test_get_intent_expressions(self):
        logger.debug("\n")
        logger.debug("Testing for 'get_intent_expressions'")
        db = ExpressionsDatabase()
        intent_expressions = db.get_intent_expressions('get-order')
        self.assertListOfString(intent_expressions)
        db.close_database_connection()
        logger.info("Testing for 'get_intent_expressions' a success!")

    def test_get_unlabeled_expressions(self):
        logger.debug("Testing for 'get_unlabeled_expressions")
        db = ExpressionsDatabase()
        unlabeled_expressions = db.get_unlabeled_expressions()
        self.assertListOfTuples(unlabeled_expressions, [int, str, str, float])
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
    
    def test_get_unlabeled_expression_by_id(self):
        logger.debug("Testing for 'get_unlabeled_expressions")
        db = ExpressionsDatabase()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        tuple_list = [tup for tup in results if tup[1] == 'This is an unlabeled expression']
        actual_unlabeled_expression = tuple_list[0]
        test_unlabeled_expression = db.get_unlabeled_expression_by_id(actual_unlabeled_expression[0])
        self.assertEqual(actual_unlabeled_expression, test_unlabeled_expression)
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
    
    def test_get_archived_expressions(self):    
        logger.debug("Testing for 'get_archived_expressions")
        db = ExpressionsDatabase()
        unlabeled_expressions = db.get_archived_expressions()
        self.assertListOfTuples(unlabeled_expressions, [int, str, str, float])
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
        
    '''
    Addition operations
    '''
    def test_add_expressions_to_intent(self):
        logger.debug("Testing for 'add_expressions_to_intent'")
        expressions_db = ExpressionsDatabase()
        intents_db = IntentsDatabase()
        intents_db.add_intent('expressionless')
        # Test for a list of expressions as argument.
        obj = expressions_db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], obj)
        # Test for a string as argument.
        obj2 = expressions_db.add_expressions_to_intent('expressionless', "Expression argument is a string")
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three", "Expression argument is a string"], obj2)
        expressions_db.delete_intent('expressionless')
        expressions_db.close_database_connection()
        intents_db.close_database_connection()
        logger.info("Testing for 'add_expressions_to_intent' a success!")

    def test_add_unlabeled_expression(self):
        logger.debug("Testing for 'add_unlabeled_expression'")
        db = ExpressionsDatabase()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        self.assertListOfTuples(results, [int, str, str, float])
        expression_id = [tup[0] for tup in results if tup[1] == 'This is an unlabeled expression']
        db.delete_unlabeled_expression(expression_id[0])
        db.close_database_connection()
        logger.info("Testing for 'add_unlabeled_expression' a success!")
       
    def test_add_archived_expressions(self):
        logger.debug("Testing for 'add_archived_expression'")
        db = ExpressionsDatabase()
        results = db.add_archived_expression('This is an archived expression', 'guess-intent', .9900)
        self.assertListOfTuples(results, [int, str, str, float])
        expression_id = [tup[0] for tup in results if tup[1] == 'This is an archived expression']
        db.delete_archived_expression(expression_id[0])
        db.close_database_connection()
        logger.info("Testing for 'add_unlabeled_expression' a success!")
    
    '''
    Deletion operations.
    '''
    def test_delete_expressions_from_intent(self):
        logger.debug("Testing for 'delete_expressions_from_intent'")
        expressions_db = ExpressionsDatabase()
        intents_db = IntentsDatabase()
        intents_db.add_intent('expressionless')
        expressions_db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = expressions_db.delete_all_intent_expressions('expressionless')
        self.assertEqual(len(obj), 0)
        intents_db.delete_intent('expressionless')
        expressions_db.close_database_connection()
        intents_db.close_database_connection()
        logger.info("Testing for 'delete_expressions_from_intent' a success!")

    def test_delete_unlabeled_expression(self):
        logger.debug("\nTesting for 'delete_unlabeled_expression'")
        test_expression = 'This is another unlabeled expression'
        db = ExpressionsDatabase()
        before_results = db.add_unlabeled_expression(test_expression, 'guess-intent', .9900)
        before_expression = [tup[1] for tup in before_results]
        self.assertIn(test_expression, before_expression)
        expression_id = [tup[0] for tup in before_results if tup[1] == test_expression]
        after_results = db.delete_unlabeled_expression(expression_id[0])
        after_expression = [tup[1] for tup in after_results]
        self.assertNotIn((test_expression,), after_expression)
        logger.info("Testing for 'delete_unlabeled_expression' a success!")
    
    def test_delete_archived_expression(self):
        logger.debug("\nTesting for 'delete_archived_expression'")
        test_expression = 'This is another archived expression'
        db = ExpressionsDatabase()
        before_results = db.add_archived_expression(test_expression, 'guess-intent', .9900)
        before_expression = [tup[1] for tup in before_results]
        self.assertIn(test_expression, before_expression)
        expression_id = [tup[0] for tup in before_results if tup[1] == test_expression]
        after_results = db.delete_archived_expression(expression_id[0])
        after_expression = [tup[1] for tup in after_results]
        self.assertNotIn((test_expression,), after_expression)
        logger.info("Testing for 'delete_unlabeled_expression' a success!")
        
    '''
    Confirmation operations
    '''
    def test_confirm_unlabeled_expression_exists(self):
        logger.debug("\nTesting for 'confirm_unlabeled_expression_exists'")
        test_expression = 'This is another unlabeled expression'
        db = ExpressionsDatabase()
        results = db.add_unlabeled_expression(test_expression, 'guess-intent', .9900)
        expression_id = [tup[0] for tup in results if tup[1] == test_expression]
        expression_exists = db.confirm_unlabeled_expression_exists(expression_id[0])
        self.assertEqual(True, expression_exists)
        db.delete_unlabeled_expression(expression_id[0])
        expression_exists = db.confirm_unlabeled_expression_exists(expression_id[0])
        self.assertEqual(False, expression_exists)
        logger.info("Testing for 'confirm_unlabeled_expression_exists' a success!")
    
    def test_confirm_archived_expression_exists(self):
        logger.debug("\nTesting for 'confirm_archived_expression_exists'")
        test_expression = 'This is another archived expression'
        db = ExpressionsDatabase()
        results = db.add_archived_expression(test_expression, 'guess-intent', .9900)
        expression_id = [tup[0] for tup in results if tup[1] == test_expression]
        expression_exists = db.confirm_archived_expression_exists(expression_id[0])
        self.assertEqual(True, expression_exists)
        db.delete_archived_expression(expression_id[0])
        expression_exists = db.confirm_archived_expression_exists(expression_id[0])
        self.assertEqual(False, expression_exists)
        logger.info("Testing for 'confirm_archived_expression_exists' a success!")
    
    
class ClassifierTest(unittest.TestCase):
    """
    Class for unit testing all methods with the nlp.clf.classification.
    
    Most methods are not functionally testable in the sense that they really only build objects.
    However they will be tested to ensure the correct objects are made via isInstance() methods
    Apart from the tokenize_text and classify_document testing, these tests may be removed since
    they're likely not providing much information.
    """
    
    @classmethod
    def setUpClass(cls):
        logger.info("Testing for Classification methods:")

    def setUp(self):
        self.builder = ClassificationModelBuilder()
        self.accesor = ClassificationModelAccessor()

    @classmethod
    def tearDownClass(cls):
        logger.info('')
    
    def test_tokenize_text(self):
        logger.debug("Testing for '_tokenize_text' of class ClassificationModelBuilder")
        test = self.builder._tokenize_text("What is the best selling item of  all  time?")
        actual = [u"what", u"be", u"the", u"best", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
        logger.info("Testing for 'tokenize_text' a success!")
    
    def test_build_classification_pipeline(self):
        logger.debug("Testing for '_build_classification_pipeline' of class ClassificationModelBuilder")
        pipeline = self.builer._build_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("Testing for 'build_classification_pipeline' a success!")
    
    def test_train_classification_pipeline(self):
        logger.debug("Testing for '_train_classification_pipeline' of class ClassificationModelBuilder")
        pipeline = self.builder._train_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("Testing for 'train_classification_pipeline' a success!")

    def test_classify(self):
        logger.debug("Testing for 'classify_document' of class Classifier")
        self.builder.update_serialized_model()
        clf = self.accesor.get_classification_pipeline()
        self.assertEqual(Classifier, type(clf))
        result = clf.classify("What is the best selling item of all time?")
        self.assertIsInstance(result, list)
        self.assertEqual("get-best-selling-items", result[0]['intent'])
        logger.info("Testing for 'classify_document' a success!")


class GazetteerTest(unittest.TestCase):
    """
        Class for unit testing all methods with the nlp.ner.gazetteer.

        Most methods are not functionally testable in the sense that they really only build objects.
        However they will be tested to ensure the correct objects are made via isInstance() methods
        Apart from the tokenize_text and classify_document testing, these tests may be removed since
        they're likely not providing much information.
        """

    @classmethod
    def setUpClass(cls):
        logger.info("Testing for Gazetteer module class methods:")

    def setUp(self):
        self.builder = GazetteerModelBuilder()
        self.accessor = GazetteerModelAccessor()

    @classmethod
    def tearDownClass(cls):
        logger.info('')

    def test_create_new_gazetteer_model(self):
        self.fail()

    def test_update_single_gazetteer_model(self):
        self.fail()

    def test_get_entities_for_training(self):
        self.fail()

    def get_gazeteers(self):
        self.fail()

    def test_search_query(self):
        self.fail()