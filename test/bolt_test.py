'''
Created on Jul 21, 2016

@author: carl
'''
import unittest
import sklearn
from classification.Classification import tokenize_text, train_classification_pipeline, build_classification_pipeline, classify_document
from database.database import NLP_Database

class CustomAssertions:
    '''
    Class for creating custom assertions used in testing the Bolt system.
    
    '''
    
    def assertListOfTuples(self, obj):
        if isinstance(obj, str):
            raise AssertionError("Returned a string argument but expected a list of tuples of length 2")
        if len(obj) == 0:
            raise AssertionError("Method failed to return a populated list.")
        else:
            assert len(obj[0]) == 2
            assert isinstance(obj[0][0], str)
            assert isinstance(obj[0][1], str)
            
    def assertListOfString(self, obj):
        if isinstance(obj, str):
            raise AssertionError("Returned a string argument but expected a list of tuples of length 2")
        if len(obj) == 0:
            raise AssertionError("Method failed to return a populated list.")
        else:
            assert isinstance(obj[0], str)
        
class NLP_Database_Test(unittest.TestCase, CustomAssertions):
    '''
    Class for unit testing all methods with the database.database.NLP_Database class
    
    '''
    
    def test_get_intents_and_expressions(self):
        db = NLP_Database()
        obj = db.get_intents_and_expressions()
        self.assertListOfTuples(obj)
        db.close_database_connection()
        
    def test_get_intents(self):
        db = NLP_Database()
        obj = db.get_intents()
        self.assertListOfString(obj)
        db.close_database_connection()
    
    def test_get_intent_expressions(self):
        db = NLP_Database()
        obj = db.get_intent_expressions('get-order')
        self.assertListOfString(obj)
        db.close_database_connection()

class Classification_Test(unittest.TestCase):
    '''
    Class for unit testing all methods with the classification.Classification.
    Most methods are not functionally testable in the sense that they really only build objects.
    However they will be tested to ensure the correct objects are made.
    '''
    
    def test_tokenize_text(self):
        test = tokenize_text("What is the best selling item of  all  time?")
        actual = [u"what", u"be", u"the", u"best", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
    
    def test_build_classification_pipeline(self):
        pipeline = build_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
    
    def test_train_classification_pipeline(self):
        pipeline = train_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        
    def test_classify_document(self):
        pipeline = train_classification_pipeline()
        result = classify_document(pipeline, "What is the best selling item of all time?")
        self.assertIsInstance(result, str)
      
      
if __name__ == '__main__':
    unittest.main()
    