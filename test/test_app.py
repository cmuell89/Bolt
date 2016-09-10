'''
Created on Jul 27, 2016

@author: carl
'''
import unittest
import json
from database.database import NLP_Database
from app import app


    
class Classification_Test(unittest.TestCase):
    """
    Class for unit testing 'Classification' routes in app.resources
    """ 
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        print("\nRoute testing for '/classification/*' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_classify_route(self):
        response = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')),
                       content_type='application/json')
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['intent'], u"get-order")
        secondResponse = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')))
        self.assertEqual(secondResponse.status_code, 415) 
        print("\n\tTesting 'POST' '/classification/classify' route a success!")
    
    def test_train_route(self):
        response = self.app.get('/classification/train')  
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['message'], "Classifier successfully trained!")
        print("\n\tTesting 'GET' '/classification/train' route a success!")
        print("\tNote: Still needs functional test")
        
class Expressions_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.db = NLP_Database()
        self.db.add_intent('test-intent')
        self.db.add_expressions_to_intent('test-intent', ["test expression one", "test expression two", "test expression three", "test expression four"])
        self.db.add_intent('delete-intent')
        self.db.add_expressions_to_intent('delete-intent', ["one","two","three","four"])
        print("\nRoute testing for 'database/expressions/<string:intent>' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        self.db.delete_intent('delete-intent')
        self.db.delete_intent('test-intent')
        self.db.close_database_connection()
    
    def test_post_expressions_to_intent_route(self):
        expressions = ["test expression five", "test expression six", "test expression seven"]
        response = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression five", result['expressions']) 
        secondResponse = self.app.post('/database/expressions/test-intent', data=json.dumps(dict(expressions=expressions)))
        self.assertEqual(secondResponse.status_code, 415) 
        print("\n\tTesting 'POST' '/database/expressions/<intent>' route a success!")
        
    def test_get_intent_expressions_route(self):
        response = self.app.get('/database/expressions/test-intent')  
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("test expression two", result['expressions']) 
        print("\n\tTesting 'GET' '/database/expressions/<intent>' route a success!")
        
    def test_delete_intent_expressions_route(self):
        response = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=False, expressions=["one"])), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("one", result['expressions'])
        secondResponse = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)), content_type='application/json')
        secondResult = json.loads(secondResponse.get_data(as_text=True))
        self.assertEqual(secondResponse.status_code, 200)
        self.assertTrue(len(secondResult['expressions'])==0, secondResult['expressions'])
        thirdResponse = self.app.delete('/database/expressions/delete-intent', data=json.dumps(dict(all=True)))
        self.assertEqual(thirdResponse.status_code, 415) 
        print("\n\tTesting 'DELETE' '/database/expressions/*' route a success!")
               
                 
class Intents_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        self.db = NLP_Database()
        self.db.add_intent('to-be-deleted')
        print("\nRoute testing for '/database/intents/' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        self.db.close_database_connection()
    
    def test_post_intent_route(self):
        intent = "some-new-intent"
        response = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("some-new-intent", result['intents'])
        self.db.delete_intent(intent)
        secondResponse = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)))
        self.assertEqual(secondResponse.status_code, 415)
        print("\n\tTesting 'POST' '/database/intents/ route a success!")
        
    def test_get_intents_route(self):
        response = self.app.get('/database/intents')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get-order", result['intents'])
        print("\n\tTesting 'GET' '/database/intents/ route a success!")
        
    def test_delete_intent_route(self):
        response = self.app.delete('/database/intents', data=json.dumps(dict(intent='to-be-deleted')), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertNotIn('to-be-deleted', result['intents'])
        print("\n\tTesting 'DELETE' '/database/intents/ route a success!")
    
