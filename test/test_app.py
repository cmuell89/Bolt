'''
Created on Jul 27, 2016

@author: carl
'''
import unittest
import json
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
        print("\nRoute testing for 'expressions/<string:intent>' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_post_expressions_to_intent_route(self):
        expressions = ["get order #12341234"]
        response = self.app.post('/database/expressions/get-order', data=json.dumps(dict(expressions=expressions)), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get order #12341234", result['expressions']) 
        secondResponse = self.app.post('/database/expressions/get-order', data=json.dumps(dict(expressions=expressions)))
        self.assertEqual(secondResponse.status_code, 415) 
        print("\n\tTesting 'POST' '/database/expressions/<intent>' route a success!")
        
    def test_get_intent_expressions_route(self):
        response = self.app.get('/database/expressions/get-order')  
        result = json.loads(response.get_data(as_text=True)) 
        self.assertEqual(response.status_code, 200)
        self.assertIn("what is order 3216", result['expressions']) 
        print("\n\tTesting 'GET' '/database/expressions/<intent>' route a success!")
                 
class Intents_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        print("\nRoute testing for '/database/intents/' endpoints:")
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_post_intent_route(self):
        intent = "some-new-intent"
        response = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)), content_type='application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("some-new-intent", result['intents'])
        secondResponse = self.app.post('/database/intents', data=json.dumps(dict(intent=intent)))
        self.assertEqual(secondResponse.status_code, 415)
        print("\nTesting 'POST' '/database/intents/ route a success!")
        
    def test_get_intents(self):
        response = self.app.get('/database/intents')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get-order", result['intents'])
        print("\nTesting 'GET' '/database/intents/ route a success!")
    
