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
from classification.classification import tokenize_text, train_classification_pipeline, build_classification_pipeline, classify_document
from database.database import NLPDatabase
from builtins import int, str

logger = logging.getLogger('BOLT.test')
    
class NLPDatabaseTest(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(self):
        logger.info("Testing for NLP_Database methods:")
    @classmethod
    def tearDownClass(self):
        logger.info('')
    
    '''
    Retrieval operations.
    '''
    def test_get_intents_and_expressions(self):
        logger.debug("Testing for 'get_intents_and_expressions'")
        db = NLPDatabase()
        intents_and_expressions = db.get_intents_and_expressions()
        self.assertListOfTuples(intents_and_expressions, [str, str])
        db.close_database_connection()
        logger.info("Testing for 'get_intents_and_expressions' a success!")
        
    def test_get_intents(self):
        logger.debug("Testing for 'get_intents'")
        db = NLPDatabase()
        intents = db.get_intents()
        self.assertListOfString(intents)
        db.close_database_connection()
        logger.info("Testing for 'get_intents' a success!")
    
    def test_get_intent_expressions(self):
        logger.debug("\n")
        logger.debug("Testing for 'get_intent_expressions'")
        db = NLPDatabase()
        intent_expressions = db.get_intent_expressions('get-order')
        self.assertListOfString(intent_expressions)
        db.close_database_connection()
        logger.info("Testing for 'get_intent_expressions' a success!")
    
    def test_get_unlabeled_expressions(self):
        logger.debug("Testing for 'get_unlabeled_expressions")
        db = NLPDatabase()
        unlabeled_expressions = db.get_unlabeled_expressions()
        self.assertListOfTuples(unlabeled_expressions, [int, str, str, float])
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
    
    def test_get_unlabeled_expression_by_id(self):
        logger.debug("Testing for 'get_unlabeled_expressions")
        db = NLPDatabase()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        tuple_list = [tup for tup in results if tup[1] == 'This is an unlabeled expression']
        actual_unlabeled_expression = tuple_list[0]
        test_unlabeled_expression = db.get_unlabeled_expression_by_id(actual_unlabeled_expression[0])
        self.assertEqual(actual_unlabeled_expression, test_unlabeled_expression)
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
        
    '''
    Addition operations
    '''
    def test_add_intent(self):
        logger.debug("Testing for 'add_intent'")
        db = NLPDatabase()
        new_list_of_intents = db.add_intent('some-new-intent')
        self.assertIn('some-new-intent', new_list_of_intents)
        db.delete_intent('some-new-intent')
        db.close_database_connection()
        logger.info("Testing for 'add_intent' a success!")
    
    def test_add_expressions_to_intent(self):
        logger.debug("Testing for 'add_expressions_to_intent'")
        db = NLPDatabase()
        db.add_intent('expressionless')
        # Test for a list of expressions as argument.
        obj = db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], obj)
        # Test for a string as argument.
        obj2 = db.add_expressions_to_intent('expressionless', "Expression argument is a string")
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three", "Expression argument is a string"], obj2)
        db.delete_intent('expressionless')
        db.close_database_connection()
        logger.info("Testing for 'add_expressions_to_intent' a success!")
    
    def test_add_unlabeled_expression(self):
        logger.debug("Testing for 'add_unlabeled_expression'")
        db = NLPDatabase()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        self.assertListOfTuples(results, [int, str, str, float])
        expression_ID = [tup[0] for tup in results if tup[1] == 'This is an unlabeled expression']
        db.delete_unlabeled_expression(expression_ID[0])
        db.close_database_connection()
        logger.info("Testing for 'add_unlabeled_expression' a success!")
        
    def test_delete_intent(self):
        logger.debug("\nTesting for 'delete_intent'")
        db = NLPDatabase()
        db.add_intent('soon-to-be-deleted')
        results = db.delete_intent('soon-to-be-deleted')
        self.assertNotIn(('soon-to-be-deleted',), results)
        logger.info("Testing for 'delete_intent' a success!")
    
    '''
    Deletion operations.
    '''
    def test_delete_expressions_from_intent(self):
        logger.debug("Testing for 'delete_expressions_from_intent'")
        db = NLPDatabase()
        db.add_intent('expressionless')
        db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = db.delete_all_intent_expressions('expressionless')
        self.assertEqual(len(obj), 0)
        db.delete_intent('expressionless')
        db.close_database_connection()
        logger.info("Testing for 'delete_expressions_from_intent' a success!")
    
    def test_delete_unlabeled_expression(self):
        logger.debug("\nTesting for 'delete_unlabeled_expression'")
        test_expression = 'This is another unlabeled expression'
        db = NLPDatabase()
        results = db.add_unlabeled_expression(test_expression, 'guess-intent', .9900)
        before_expression = [tup[1] for tup in results]
        self.assertIn(test_expression, before_expression)
        expressionID = [tup[0] for tup in results if tup[1] == test_expression]
        after = db.delete_unlabeled_expression(expressionID[0])
        after_expression = [tup[1] for tup in results]
        self.assertNotIn((test_expression,), after_expression)
        logger.info("Testing for 'delete_unlabeled_expression' a success!")
    
    def test_confirm_intent_exists(self):
        logger.debug("\nTesting for 'confirm_intent_exists'")
        db = NLPDatabase()
        db.add_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(True, intent_exists)
        db.delete_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(False, intent_exists)
        logger.info("Testing for 'confirm_intent_exists' a success!")
    
    
class ClassifierTest(unittest.TestCase):
    """
    Class for unit testing all methods with the classification.classification.
    
    Most methods are not functionally testable in the sense that they really only build objects.
    However they will be tested to ensure the correct objects are made via isInstance() methods
    Apart from the tokenize_tect testing, these tests may be removed since they're likely not providing much information.
    """
    
    @classmethod
    def setUpClass(self):
        logger.info("Testing for Classification methods:")
        
    @classmethod
    def tearDownClass(self):
        logger.info('')
    
    def test_tokenize_text(self):
        logger.debug("Testing for 'tokenize_text'")
        test = tokenize_text("What is the best selling item of  all  time?")
        actual = [u"what", u"be", u"the", u"best", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
        logger.info("Testing for 'tokenize_text' a success!")
    
    def test_build_classification_pipeline(self):
        logger.debug("Testing for 'build_classification_pipeline'")
        pipeline = build_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("Testing for 'build_classification_pipeline' a success!")
    
    def test_train_classification_pipeline(self):
        logger.debug("Testing for 'train_classification_pipeline'")
        pipeline = train_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("Testing for 'train_classification_pipeline' a success!")
        
    def test_classify_document(self):
        logger.debug("Testing for 'classify_document'")
        pipeline = train_classification_pipeline()
        result = classify_document(pipeline, "What is the best selling item of all time?")
        self.assertIsInstance(result, list)
        logger.info("Testing for 'classify_document' a success!")
        

    