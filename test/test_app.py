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
from database.database import NLP_Database
from app import app

logger = logging.getLogger('BOLT.test')
    
class Classification_Test(unittest.TestCase):
    """
    Class for unit testing 'Classification' routes in app.resources
    """ 
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.accessToken = os.environ.get('ACCESS_TOKEN')
        logger.info("Route testing for '/classification/*' endpoints:\n")
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_classify_route(self):
        logger.info("Testing 'POST' '/classification/classify'")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')),
                       headers=testHeaders)
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        print()
        print(result)
        print(result['intents'])
        print(type(result['intents']))
        print()
        self.assertEqual(result['intents'][0]['intent'], u"get-order")
        secondTestHeaders = Headers()
        secondTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        secondResponse = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')), headers=secondTestHeaders)
        self.assertEqual(secondResponse.status_code, 415) 
        logger.info("Testing 'POST' '/classification/classify' route a success!\n")
    
    def test_train_route(self):
        logger.info("Testing 'GET' '/classification/train'")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.get('/classification/train/nb', headers=testHeaders)  
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['message'], "Classifier successfully trained: nb")
        secondTestHeaders = Headers()
        secondTestHeaders.add('Content-Type', 'application/json')
        secondTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        secondResponse = self.app.get('/classification/train/svm', headers=testHeaders)  
        self.assertEqual(secondResponse.status_code, 200) 
        secondResult = json.loads(secondResponse.get_data(as_text=True))
        self.assertEqual(secondResult['message'], "Classifier successfully trained: svm")
        logger.info("Testing 'GET' '/classification/train' route a success!")
        logger.info("Note: Still needs functional test\n")
        
class Expressions_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.accessToken = os.environ.get("ACCESS_TOKEN")
        self.db = NLP_Database()
        self.db.add_intent('test-intent')
        self.db.add_expressions_to_intent('test-intent', ["test expression one", "test expression two", "test expression three", "test expression four"])
        self.db.add_intent('delete-intent')
        self.db.add_expressions_to_intent('delete-intent', ["one", "two", "three", "four"])
        logger.info("Route testing for 'database/expressions/<string:intent>' endpoints:\n")
        
    @classmethod
    def tearDownClass(self):
        self.db.delete_intent('delete-intent')
        self.db.delete_intent('test-intent')
        self.db.close_database_connection()
    
    def test_post_expressions_to_intent_route(self):
        logger.info("Testing 'POST' '/database/expressions/<intent>'")
        expressions = ["test expression five", "test expression six", "test expression seven"]
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=testHeaders)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression five", result['expressions']) 
        secondTestHeaders = Headers()
        secondTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        secondResponse = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), headers=secondTestHeaders)
        self.assertEqual(secondResponse.status_code, 415) 
        logger.info("Testing 'POST' '/database/expressions/<intent>' route a success!\n")
        
    def test_get_intent_expressions_route(self):
        logger.info("Testing 'GET' '/database/expressions/<intent>'")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.get('/database/expressions/test-intent', headers=testHeaders)  
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression two", result['expressions']) 
        logger.info("Testing 'GET' '/database/expressions/<intent>' route a success!\n")
        
    def test_delete_intent_expressions_route(self):
        logger.info("Testing 'DELETE' '/database/expressions/*'")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=False, expressions=["one"])), headers=testHeaders)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("one", result['expressions'])
        secondTestHeaders = Headers()
        secondTestHeaders.add('Content-Type', 'application/json')
        secondTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        secondResponse = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=secondTestHeaders)
        secondResult = json.loads(secondResponse.get_data(as_text=True))
        self.assertEqual(secondResponse.status_code, 422)
        thirdTestHeaders = Headers()
        thirdTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        thirdResponse = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), headers=thirdTestHeaders)
        self.assertEqual(thirdResponse.status_code, 415) 
        logger.info("Testing 'DELETE' '/database/expressions/*' route a success!\n")
               
                 
class Intents_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.accessToken = os.environ.get('ACCESS_TOKEN')
        self.db = NLP_Database()
        self.db.add_intent('to-be-deleted')
        logger.info("Route testing for '/database/intents/' endpoints:\n")
        
    @classmethod
    def tearDownClass(self):
        self.db.close_database_connection()
    
    def test_post_intent_route(self):
        logger.info("Testing 'POST' '/database/intents/")
        intent = "some-new-intent"
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=testHeaders)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("some-new-intent", result['intents'])
        self.db.delete_intent(intent)
        secondTestHeaders = Headers()
        secondTestHeaders.add('Authorization', 'Token ' + self.accessToken)
        secondResponse = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), headers=secondTestHeaders)
        self.assertEqual(secondResponse.status_code, 415)
        logger.info("Testing 'POST' '/database/intents/ route a success!\n")
        
    def test_get_intents_route(self):
        logger.info("Testing 'GET' '/database/intents/")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.get('/database/intents', headers=testHeaders)
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get-order", result['intents'])
        logger.info("Testing 'GET' '/database/intents/ route a success!\n")
        
    def test_delete_intent_route(self):
        logger.info("Testing 'DELETE' '/database/intents/")
        testHeaders = Headers()
        testHeaders.add('Content-Type', 'application/json')
        testHeaders.add('Authorization', 'Token ' + self.accessToken)
        response = self.app.delete('/database/intents', data=json.dumps(dict(intent='to-be-deleted')), headers=testHeaders)
        result = json.loads(response.get_data(as_text=True))
        self.assertNotIn('to-be-deleted', result['intents'])
        logger.info("Testing 'DELETE' '/database/intents/ route a success!\n")
    
