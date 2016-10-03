'''
Created on Jul 21, 2016

@author: Carl Mueller

Unit tests for general Bolt module functions, classes and methods. 

These tests are either too succinct or non-specific to warrant their own module. 
'''
import unittest
import sklearn
import settings
import logging
from utils.custom_assertions import CustomAssertions
from classification.classification import tokenize_text, train_classification_pipeline, build_classification_pipeline, classify_document
from database.database import NLP_Database
from builtins import int, str

logger = logging.getLogger('BOLT.test')
    
class NLP_Database_Test(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(self):
        logger.info('')
        logger.info("Testing for NLP_Database methods:")
    @classmethod
    def tearDownClass(self):
        pass
    
    
    def test_get_intents_and_expressions(self):
        logger.debug("Testing for 'get_intents_and_expressions'")
        db = NLP_Database()
        intentsAndExpressions = db.get_intents_and_expressions()
        self.assertListOfTuples(intentsAndExpressions, [str, str])
        db.close_database_connection()
        logger.info("Testing for 'get_intents_and_expressions' a success!")
        
    def test_get_intents(self):
        logger.debug("Testing for 'get_intents'")
        db = NLP_Database()
        intents = db.get_intents()
        self.assertListOfString(intents)
        db.close_database_connection()
        logger.info("Testing for 'get_intents' a success!")
    
    def test_get_intent_expressions(self):
        logger.debug("\n")
        logger.debug("Testing for 'get_intent_expressions'")
        db = NLP_Database()
        intentExpressions = db.get_intent_expressions('get-order')
        self.assertListOfString(intentExpressions)
        db.close_database_connection()
        logger.info("Testing for 'get_intent_expressions' a success!")
    
    def test_get_unlabeled_expressions(self):
        logger.debug("Testing for 'get_unlabeled_expressions")
        db = NLP_Database()
        unlabeledExpressions = db.get_unlabeled_expressions()
        self.assertListOfTuples(unlabeledExpressions, [int, str, str])
        db.close_database_connection()
        logger.info("Testing for 'get_unlabled_expressions' a success!")
    
    def test_add_intent(self):
        logger.debug("Testing for 'add_intent'")
        db = NLP_Database()
        newListOfIntents = db.add_intent('some-new-intent')
        self.assertIn('some-new-intent', newListOfIntents)
        db.delete_intent('some-new-intent')
        db.close_database_connection()
        logger.info("Testing for 'add_intent' a success!")
    
    def test_add_expressions_to_intent(self):
        logger.debug("Testing for 'add_expressions_to_intent'")
        db = NLP_Database()
        db.add_intent('expressionless')
        obj = db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], obj)
        db.delete_intent('expressionless')
        db.close_database_connection()
        logger.info("Testing for 'add_expressions_to_intent' a success!")
    
    def test_add_unlabeled_expression(self):
        logger.debug("Testing for 'add_unlabeled_expression'")
        db = NLP_Database()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent')
        self.assertListOfTuples(results, [int, str, str])
        expressionID = [tup[0] for tup in results if tup[1] == 'This is an unlabeled expression']
        db.delete_unlabeled_expression(expressionID[0])
        db.close_database_connection()
        logger.info("Testing for 'add_unlabeled_expression' a success!")
        
        
    def test_delete_intent(self):
        logger.debug("\nTesting for 'delete_intent'")
        db = NLP_Database()
        db.add_intent('soon-to-be-deleted')
        results = db.delete_intent('soon-to-be-deleted')
        self.assertNotIn(('soon-to-be-deleted',), results)
        logger.info("Testing for 'delete_intent' a success!")
    
    def test_delete_expressions_from_intent(self):
        logger.debug("Testing for 'delete_expressions_from_intent'")
        db = NLP_Database()
        db.add_intent('expressionless')
        db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = db.delete_all_intent_expressions('expressionless')
        self.assertEqual(len(obj), 0)
        db.delete_intent('expressionless')
        db.close_database_connection()
        logger.info("Testing for 'delete_expressions_from_intent' a success!")
    
    def test_delete_unlabeled_expression(self):
        logger.debug("\nTesting for 'delete_unlabeled_expression'")
        testExpression = 'This is another unlabeled expression'
        db = NLP_Database()
        results = db.add_unlabeled_expression(testExpression, 'guess-intent')
        beforeExpression = [tup[1] for tup in results]
        self.assertIn(testExpression, beforeExpression)
        expressionID = [tup[0] for tup in results if tup[1] == testExpression]
        after = db.delete_unlabeled_expression(expressionID[0])
        afterExpressions = [tup[1] for tup in results]
        self.assertNotIn((testExpression,), afterExpressions)
        logger.info("Testing for 'delete_unlabeled_expression' a success!")
    

        
class Classifier_Test(unittest.TestCase):
    """
    Class for unit testing all methods with the classification.classification.
    
    Most methods are not functionally testable in the sense that they really only build objects.
    However they will be tested to ensure the correct objects are made via isInstance() methods
    Apart from the tokenize_tect testing, these tests may be removed since they're likely not providing much information.
    """
    
    @classmethod
    def setUpClass(self):
        logger.info('')
        logger.info("Testing for Classification methods:")
        
    @classmethod
    def tearDownClass(self):
        pass
    
    
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
        

    