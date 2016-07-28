'''
Created on Jul 21, 2016

@author: Carl Mueller

Unit tests for general Bolt module functions, classes and methods. 

These tests are either too succinct or non-specific to warrant their own module. 
'''
import unittest
import sklearn
from utils.custom_assertions import CustomAssertions
from classification.Classification import tokenize_text, train_classification_pipeline, build_classification_pipeline, classify_document
from database.database import NLP_Database

    
class NLP_Database_Test(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    
    def test_get_intents_and_expressions(self):
        print("\nTesting get_intents_and_expressions...")
        db = NLP_Database()
        obj = db.get_intents_and_expressions()
        self.assertListOfTuples(obj)
        db.close_database_connection()
        print("Success!")
        
    def test_get_intents(self):
        print("\nTesting get_intents...")
        db = NLP_Database()
        obj = list(map(lambda x: x[0], db.get_intents())) 
        self.assertListOfString(obj)
        db.close_database_connection()
        print("Success!")
    
    def test_get_intent_expressions(self):
        print("\nTesting get_intent_expressions...")
        db = NLP_Database()
        obj =list(map(lambda x: x[0], db.get_intent_expressions('get-order')))
        self.assertListOfString(obj)
        db.close_database_connection()
        print("Success!")
        
    def test_add_intent(self):
        print("\nTesting add_intent...")
        db = NLP_Database()
        obj = list(map(lambda x: x[0], db.add_intent('some-new-intent')))
        self.assertIn('some-new-intent', obj)
        db.close_database_connection()
        print("Success!")
        
    def test_delete_intent(self):
        print("\nTesting delete_intent...")
        db = NLP_Database()
        db.add_intent('soon-to-be-deleted')
        obj = db.delete_intent('soon-to-be-deleted')
        self.assertNotIn('soon-to-be-deleted', obj)
        print("Success!")
    
    def test_delete_expressions_from_intent(self):
        print("\nTesting delete_expressions_from_intent...")
        db = NLP_Database()
        db.add_intent('expressionless')
        db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = db.delete_all_intent_expressions('expressionless')
        self.assertListOfTuples(obj)
        for tup in obj:
            self.assertNotEqual('expressionless', tup[0])
        db.delete_intent('expressionless')
        db.close_database_connection()
        print("Success!")
    
    def test_add_expressions_to_intent(self):
        print("\nTesting add_expressions_to_intent...")
        db = NLP_Database()
        db.add_intent('expressionless')
        query = db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = list(map(lambda x: x[0], query))
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], obj)
        db.close_database_connection()
        print("Success!")

        
class Classifier_Test(unittest.TestCase):
    """
    Class for unit testing all methods with the classification.Classification.
    
    Most methods are not functionally testable in the sense that they really only build objects.
    However they will be tested to ensure the correct objects are made via isInstance() methods
    Apart from the tokenize_tect testing, these tests may be removed since they're likely not providing much information.
    """
    
    def test_tokenize_text(self):
        print("\nTesting tokenize_text...")
        test = tokenize_text("What is the best selling item of  all  time?")
        actual = [u"what", u"be", u"the", u"best", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
        print("Success!")
    
    def test_build_classification_pipeline(self):
        print("\nTesting build_classification_pipeline...")
        pipeline = build_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        print("Success!")
    
    def test_train_classification_pipeline(self):
        print("\nTesting train_classification_pipeline...")
        pipeline = train_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        print("Success!")
        
    def test_classify_document(self):
        print("\nTesting classify_document...")
        pipeline = train_classification_pipeline()
        result = classify_document(pipeline, "What is the best selling item of all time?")
        self.assertIsInstance(result, str)
        print("Success!")
        

    