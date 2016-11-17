'''
Created on Jul 27, 2016

@author: Carl Mueller
'''
import os
import unittest
import json
import settings
import logging
from werkzeug.datastructures import Headers
from database.database import IntentsDatabaseEngine, ExpressionsDatabaseEngine
from app import app

logger = logging.getLogger('BOLT.test')


class ClassificationTest(unittest.TestCase):
    """
    Class for unit testing 'Classification' routes in restful_api.py.
    """ 
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.access_token = os.environ.get('ACCESS_TOKEN')
        logger.info("TEST SUITE: ClassificationTest <API>")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: ClassificationTest <API>\n")

    def test_classify_route(self):
        logger.debug("TEST: 'POST' '/classification/analyze'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = ClassificationTest.app.post('/classification/analyze',
                                               data=json.dumps(dict(query='What is order 2313?', id='1234')),
                                               headers=test_headers)
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['classification'][0]['intent'], u"get-order")
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = ClassificationTest.app.post('/classification/analyze',
                                                      data=json.dumps(dict(query='What is order 2313?')),
                                                      headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415)
        logger.info("TEST PASS: 'POST' '/classification/analyze'")
    
    def test_train_route(self):
        logger.debug("TEST: 'GET' '/classification/train'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = ClassificationTest.app.get('/classification/train/nb', headers=test_headers)
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['message'], "Classifier successfully trained: nb")
        second_test_headers = Headers()
        second_test_headers.add('Content-Type', 'application/json')
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = ClassificationTest.app.get('/classification/train/svm', headers=second_test_headers)
        self.assertEqual(second_response.status_code, 200) 
        second_result = json.loads(second_response.get_data(as_text=True))
        self.assertEqual(second_result['message'], "Classifier successfully trained: svm")
        logger.info("TEST PASS: 'GET' '/classification/train'")


class ExpressionsTest(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in restful_api.py.
    """       
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.access_token = os.environ.get("ACCESS_TOKEN")
        cls.intents_db = IntentsDatabaseEngine()
        cls.expressions_db = ExpressionsDatabaseEngine()
        cls.intents_db.add_intent('test-intent')
        cls.expressions_db.add_expressions_to_intent('test-intent',
                                                      ["test expression one", "test expression two",
                                                       "test expression three",
                                                       "test expression four"])
        cls.intents_db.add_intent('delete-intent')
        cls.expressions_db.add_expressions_to_intent('delete-intent', ["one", "two", "three", "four"])
        logger.info("TEST SUITE: ExpressionsTest <API>")

    @classmethod
    def tearDownClass(cls):
        cls.intents_db.delete_intent('delete-intent')
        cls.intents_db.delete_intent('test-intent')
        cls.intents_db.close_database_connection()
        cls.expressions_db.close_database_connection()
        logger.info("TEST SUITE PASS: ExpressionsTest <API>\n")

    def test_post_expressions_to_intent_route(self):
        logger.debug("TEST: 'POST' '/database/expressions/<intent>'")
        expressions = ["test expression five", "test expression six", "test expression seven"]
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + ExpressionsTest.access_token)
        response = ExpressionsTest.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression five", result['expressions']) 
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + ExpressionsTest.access_token)
        second_response = ExpressionsTest.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415) 
        logger.info("TEST PASS: 'POST' '/database/expressions/<intent>'")
        
    def test_get_intent_expressions_route(self):
        logger.debug("TEST: 'GET' '/database/expressions/<intent>'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + ExpressionsTest.access_token)
        response = ExpressionsTest.app.get('/database/expressions/test-intent', headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression two", result['expressions']) 
        logger.info("TEST PASS: 'GET' '/database/expressions/<intent>'")
        
    def test_delete_intent_expressions_route(self):
        logger.debug("TEST: 'DELETE' '/database/expressions/*'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = ExpressionsTest.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=False, expressions=["one"])), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("one", result['expressions'])
        second_test_headers = Headers()
        second_test_headers.add('Content-Type', 'application/json')
        second_test_headers.add('Authorization', 'Token ' + ExpressionsTest.access_token)
        second_response = ExpressionsTest.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 422)
        third_test_headers = Headers()
        third_test_headers.add('Authorization', 'Token ' + ExpressionsTest.access_token)
        third_response = ExpressionsTest.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=third_test_headers)
        self.assertEqual(third_response.status_code, 415) 
        logger.info("TEST PASS: 'DELETE' '/database/expressions/*'")


class UnlabeledExpressionsTest(unittest.TestCase):
    """
    Class for unit testing 'UnlabeledExpressions" routes in restful_api.py.
    """
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.access_token = os.environ.get("ACCESS_TOKEN")
        cls.db = ExpressionsDatabaseEngine()
        cls.post_unlabeled_test_expression = "get_unlabeled_test_expression"
        cls.db_results = cls.db.add_unlabeled_expression(cls.post_unlabeled_test_expression, 'guess-intent', .99)
        cls.unlabeled_test_expression_ID = [tup[0] for tup in cls.db_results if
                                             tup[1] == cls.post_unlabeled_test_expression]
        logger.info("TEST SUITE: UnlabeldExpressionsTest <API>")
    
    @classmethod
    def tearDownClass(cls):
        cls.db.delete_unlabeled_expression(cls.unlabeled_test_expression_ID[0])
        cls.db.close_database_connection()
        logger.info("TEST PASS: UnlabeldExpressionsTest <API>\n")

    def test_post_unlabeled_expression(self):
        logger.debug("TEST: 'POST' '/database/unlabeled_expressions'")
        expression = UnlabeledExpressionsTest.post_unlabeled_test_expression
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + UnlabeledExpressionsTest.access_token)
        response = UnlabeledExpressionsTest.app.post('/database/unlabeled_expressions', data=json.dumps(dict(expression=expression, estimated_intent="guess-intent", estimated_confidence=.99)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        list_of_expressions = [exp['expression'] for exp in result['unlabeled_expressions']]
        self.assertIn(expression, list_of_expressions) 
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + UnlabeledExpressionsTest.access_token)
        second_response = UnlabeledExpressionsTest.app.post('/database/unlabeled_expressions', data=json.dumps(dict(expression=expression, estimated_intent="guess-intent", estimated_confidence=.99)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415) 
        logger.info("TEST PASS: 'POST' '/database/unlabeled_expressions'")
    
    def test_get_unlabeled_expressions(self):
        logger.debug("TEST: 'GET' '/database/unlabeled_expressions'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + UnlabeledExpressionsTest.access_token)
        db_results = UnlabeledExpressionsTest.db.add_unlabeled_expression("add unlabeled expression test", "guess-intent", .99)
        expression_ID = [tup[0] for tup in db_results if tup[1] == "add unlabeled expression test"]
        response = UnlabeledExpressionsTest.app.get('/database/unlabeled_expressions', data=json.dumps(dict(id=expression_ID[0])), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        list_of_expressions = [exp['expression'] for exp in result['unlabeled_expressions']]
        self.assertEqual(response.status_code, 200)
        self.assertIn("add unlabeled expression test", list_of_expressions)
        UnlabeledExpressionsTest.db.delete_unlabeled_expression(expression_ID[0])
        logger.info("TEST PASS: 'GET' '/database/unlabeled_expressions'")
        
    def test_delete_unlabeled_expression(self):
        logger.debug("TEST: 'DELETE' '/database/unlabeled_expressions")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + UnlabeledExpressionsTest.access_token)
        ## Add an expression, get the id, delete it, db.confirm exists
        db_results = UnlabeledExpressionsTest.db.add_unlabeled_expression("add unlabeled expression test", "guess-intent", .99)
        expression_ID = [tup[0] for tup in db_results if tup[1] == "add unlabeled expression test"]
        response = UnlabeledExpressionsTest.app.delete('/database/unlabeled_expressions', data=json.dumps(dict(id=expression_ID[0])), headers=test_headers)
        self.assertEqual(response.status_code, 200)
        exists = UnlabeledExpressionsTest.db.confirm_unlabeled_expression_exists(expression_ID[0])
        self.assertNotEqual(True, exists)
        logger.info("TEST PASS: 'DELETE' '/database/unlabeled_expressions")


class ArchivedExpressionsTest(unittest.TestCase):
    """
    Class for unit testing 'UnlabeledExpressions" routes in restful_api.py.
    """
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.access_token = os.environ.get("ACCESS_TOKEN")
        cls.db = ExpressionsDatabaseEngine()
        cls.post_archived_test_expression = "post_archived_test_expression"
        cls.db_results = cls.db.add_archived_expression(cls.post_archived_test_expression, 'guess-intent', .99)
        cls.archived_test_expression_ID = [tup[0] for tup in cls.db_results if
                                           tup[1] == cls.post_archived_test_expression]
        logger.info("TEST SUITE: ArchivedExpressionsTest <API>")

    @classmethod
    def tearDownClass(cls):
        cls.db.close_database_connection()
        logger.info("TEST SUITE PASS: ArchivedExpressionsTest <API>\n")

    def test_post_archived_expression(self):
        logger.debug("TEST: 'POST' '/database/archived_expressions'")
        expression = ArchivedExpressionsTest.post_archived_test_expression
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + ArchivedExpressionsTest.access_token)
        response = ArchivedExpressionsTest.app.post('/database/archived_expressions', data=json.dumps(dict(expression=expression, estimated_intent="guess-intent", estimated_confidence=.99)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        list_of_expressions = [exp['expression'] for exp in result['archived_expressions']]
        self.assertIn(expression, list_of_expressions) 
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + ArchivedExpressionsTest.access_token)
        second_response = ArchivedExpressionsTest.app.post('/database/archived_expressions', data=json.dumps(dict(expression=expression, estimated_intent="guess-intent", estimated_confidence=.99)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415) 
        logger.info("TEST PASS: 'POST' '/database/archived_expressions'")
    
    def test_get_archived_expressions(self):
        logger.debug("TEST: 'GET' '/database/archived_expressions'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + ArchivedExpressionsTest.access_token)
        db_results = ArchivedExpressionsTest.db.add_archived_expression("add archived expression test", "guess-intent", .99)
        expression_ID = [tup[0] for tup in db_results if tup[1] == "add archived expression test"]
        response = ArchivedExpressionsTest.app.get('/database/archived_expressions', data=json.dumps(dict(id=expression_ID[0])), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        list_of_expressions = [exp['expression'] for exp in result['archived_expressions']]
        self.assertEqual(response.status_code, 200)
        self.assertIn("add archived expression test", list_of_expressions)
        ArchivedExpressionsTest.db.delete_unlabeled_expression(expression_ID[0])
        logger.info("TEST PASS: 'GET' '/database/archived_expressions'")
        
    def test_delete_archived_expression(self):
        logger.debug("TEST: 'DELETE' '/database/archived_expressions")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + ArchivedExpressionsTest.access_token)
        db_results = ArchivedExpressionsTest.db.add_archived_expression("delete archived expression test", "guess-intent", .99)
        expression_ID = [tup[0] for tup in db_results if tup[1] == "delete archived expression test"]
        response = ArchivedExpressionsTest.app.delete('/database/archived_expressions', data=json.dumps(dict(id=expression_ID[0])), headers=test_headers)
        self.assertEqual(response.status_code, 200)
        exists = ArchivedExpressionsTest.db.confirm_archived_expression_exists(expression_ID[0])
        self.assertNotEqual(True, exists)
        logger.info("TEST PASS: 'DELETE' '/database/archived_expressions")
    
         
class IntentsTest(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in restful_api.py.
    """       
    @classmethod
    def setUpClass(cls):
        cls.app = app.test_client()
        cls.app.testing = True
        cls.access_token = os.environ.get('ACCESS_TOKEN')
        cls.db = IntentsDatabaseEngine()
        cls.db.add_intent('to-be-deleted')
        logger.info("TEST SUITE: IntentsTest <API>")

    @classmethod
    def tearDownClass(cls):
        cls.db.close_database_connection()
        logger.info("TEST SUITE PASS: IntentsTest <API>\n")
    
    def test_post_intent_route(self):
        logger.debug("TEST: 'POST' '/database/intents/")
        intent = "some-new-intent"
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + IntentsTest.access_token)
        response = IntentsTest.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("some-new-intent", result['intents'])
        IntentsTest.db.delete_intent(intent)
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + IntentsTest.access_token)
        second_response = IntentsTest.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415)
        logger.info("TEST PASS: 'POST' '/database/intents/")
        
    def test_get_intents_route(self):
        logger.debug("TEST: 'GET' '/database/intents/")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + IntentsTest.access_token)
        response = IntentsTest.app.get('/database/intents', headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get-order", result['intents'])
        logger.info("TEST PASS: 'GET' '/database/intents/")
        
    def test_delete_intent_route(self):
        logger.debug("TEST: 'DELETE' '/database/intents/")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + IntentsTest.access_token)
        response = IntentsTest.app.delete('/database/intents', data=json.dumps(dict(intent='to-be-deleted')), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertNotIn('to-be-deleted', result['intents'])
        logger.info("TEST: 'DELETE' '/database/intents/")

