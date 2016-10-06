'''
Created on Jul 27, 2016

@author: carl
'''
import os
import unittest
import json
import settings
import logging
from werkzeug import Headers
from database.database import NLPDatabase
from app import app

logger = logging.getLogger('BOLT.test')
    
class ClassificationTest(unittest.TestCase):
    """
    Class for unit testing 'Classification' routes in app.resources
    """ 
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.access_token = os.environ.get('ACCESS_TOKEN')
        logger.info("Route testing for '/classification/*' endpoints:")
  
    @classmethod
    def tearDownClass(self):
        logger.info('')
    
    def test_classify_route(self):
        logger.debug("Testing 'POST' '/classification/classify'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')),
                       headers=test_headers)
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['intents'][0]['intent'], u"get-order")
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        secondResponse = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')), headers=second_test_headers)
        self.assertEqual(secondResponse.status_code, 415) 
        logger.info("Testing 'POST' '/classification/classify' route a success!")
    
    def test_train_route(self):
        logger.debug("Testing 'GET' '/classification/train'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.get('/classification/train/nb', headers=test_headers)  
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['message'], "Classifier successfully trained: nb")
        second_test_headers = Headers()
        second_test_headers.add('Content-Type', 'application/json')
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = self.app.get('/classification/train/svm', headers=second_test_headers)  
        self.assertEqual(second_response.status_code, 200) 
        second_result = json.loads(second_response.get_data(as_text=True))
        self.assertEqual(second_result['message'], "Classifier successfully trained: svm")
        logger.info("Testing 'GET' '/classification/train' route a success!")
        logger.info("Note: Still needs functional test")
        
class ExpressionsTest(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.access_token = os.environ.get("ACCESS_TOKEN")
        self.db = NLPDatabase()
        self.db.add_intent('test-intent')
        self.db.add_expressions_to_intent('test-intent', ["test expression one", "test expression two", "test expression three", "test expression four"])
        self.db.add_intent('delete-intent')
        self.db.add_expressions_to_intent('delete-intent', ["one", "two", "three", "four"])
        logger.info("Route testing for 'database/expressions/<string:intent>' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        self.db.delete_intent('delete-intent')
        self.db.delete_intent('test-intent')
        self.db.close_database_connection()
        logger.info('')
    
    def test_post_expressions_to_intent_route(self):
        logger.debug("Testing 'POST' '/database/expressions/<intent>'")
        expressions = ["test expression five", "test expression six", "test expression seven"]
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression five", result['expressions']) 
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415) 
        logger.info("Testing 'POST' '/database/expressions/<intent>' route a success!")
        
    def test_get_intent_expressions_route(self):
        logger.debug("Testing 'GET' '/database/expressions/<intent>'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.get('/database/expressions/test-intent', headers=test_headers)  
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression two", result['expressions']) 
        logger.info("Testing 'GET' '/database/expressions/<intent>' route a success!")
        
    def test_delete_intent_expressions_route(self):
        logger.debug("Testing 'DELETE' '/database/expressions/*'")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=False, expressions=["one"])), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("one", result['expressions'])
        second_test_headers = Headers()
        second_test_headers.add('Content-Type', 'application/json')
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 422)
        third_test_headers = Headers()
        third_test_headers.add('Authorization', 'Token ' + self.access_token)
        third_response = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=third_test_headers)
        self.assertEqual(third_response.status_code, 415) 
        logger.info("Testing 'DELETE' '/database/expressions/*' route a success!")
               
                 
class IntentsTest(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.access_token = os.environ.get('ACCESS_TOKEN')
        self.db = NLPDatabase()
        self.db.add_intent('to-be-deleted')
        logger.info("Route testing for '/database/intents/' endpoints:")

        
    @classmethod
    def tearDownClass(self):
        self.db.close_database_connection()
        logger.info('')
    
    def test_post_intent_route(self):
        logger.debug("Testing 'POST' '/database/intents/")
        intent = "some-new-intent"
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("some-new-intent", result['intents'])
        self.db.delete_intent(intent)
        second_test_headers = Headers()
        second_test_headers.add('Authorization', 'Token ' + self.access_token)
        second_response = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=second_test_headers)
        self.assertEqual(second_response.status_code, 415)
        logger.info("Testing 'POST' '/database/intents/ route a success!")
        
    def test_get_intents_route(self):
        logger.debug("Testing 'GET' '/database/intents/")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.get('/database/intents', headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get-order", result['intents'])
        logger.info("Testing 'GET' '/database/intents/ route a success!")
        
    def test_delete_intent_route(self):
        logger.debug("Testing 'DELETE' '/database/intents/")
        test_headers = Headers()
        test_headers.add('Content-Type', 'application/json')
        test_headers.add('Authorization', 'Token ' + self.access_token)
        response = self.app.delete('/database/intents', data=json.dumps(dict(intent='to-be-deleted')), headers=test_headers)
        result = json.loads(response.get_data(as_text=True))
        self.assertNotIn('to-be-deleted', result['intents'])
        logger.info("Testing 'DELETE' '/database/intents/ route a success!")
    
