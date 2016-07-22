'''
Created on Jul 21, 2016

@author: carl
'''
import unittest
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
        
class Database_Test(unittest.TestCase, CustomAssertions):
    
    
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
        
if __name__ == '__main__':
    unittest.main()