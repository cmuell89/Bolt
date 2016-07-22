'''
Created on Jul 21, 2016

@author: carl
'''
import unittest
from database.database import NLP_Database



class CustomAssertions:
    '''
    Class for creating custom asserstions used in testing the Bolt system.
    
    '''
    
    def assertListOfTuples(self, obj):
        if isinstance(obj, str):
            raise AssertionError("Returned a string argument but expected a list of tuples of length 2")
        if len(obj) == 0:
            raise AssertionError("Method failed to return a populated list.")
        else:
            assert len(obj[0]) == 2
            
        
class Database_Test(unittest.TestCase, CustomAssertions):
    
    def test_get_intents_and_expressions(self):
        db = NLP_Database()
        obj = db.get_intents_and_expressions()
        self.assertListOfTuples(obj)


if __name__ == '__main__':
    unittest.main()