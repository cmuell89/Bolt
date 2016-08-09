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
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_classify_route(self):
        print("\nTesting 'POST' '/classification/classify' route...")
        response = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')),
                       content_type = 'application/json')
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['intent'], u"get-order")
        secondResponse = self.app.post('/classification/classify', data=json.dumps(dict(query='What is order 2313?')))
        self.assertEqual(secondResponse.status_code, 415) 
        print("Success!")
    
    def test_train_route(self):
        print("\nTesting 'GET' '/classification/train' route...")
        print("Note: Still needs functional test")
        response = self.app.get('/classification/train')  
        self.assertEqual(response.status_code, 200) 
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(result['message'], "Classifier successfully trained!")
        print("Success!")
        
class Expressions_Test(unittest.TestCase):
    """
    Class for unit testing 'Expressions' routes in app.resources
    """       
    @classmethod
    def setUpClass(self):
        self.app = app.test_client()
        self.app.testing = True
        
    @classmethod
    def tearDownClass(self):
        pass
    
    def test_add_expressions_to_intent_route(self):
        print("\nTesting 'POST' '/expressions/?intent=<intent>' route...")
        expressions = ["get order #12341234"]
        response = self.app.post('/expressions/get-order', data=json.dumps(dict(expressions=expressions)), content_type = 'application/json')
        result = json.loads(response.get_data(as_text=True))
        self.assertEqual(response.status_code, 200)
        self.assertIn("get order #12341234", result['expressions']) 
        secondResponse = self.app.post('/expressions/get-order', data=json.dumps(dict(expressions=expressions)))
        self.assertEqual(secondResponse.status_code, 415) 
        print("Success!")
        
    def test_get_intent_expressions_route(self):
        print("\nTesting 'GET' '/expressions/<intent>' route...")
        response = self.app.get('/expressions/get-order')  
        result = json.loads(response.get_data(as_text=True)) 
        self.assertEqual(response.status_code, 200)
        self.assertIn("what is order 3216", result['expressions']) 
        print("Success!")
                 