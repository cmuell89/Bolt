'''
Created on Jul 21, 2016

@author: carl
'''
import unittest

from database.database import NLP_Database

class Database_Test(unittest.TestCase):
    def set_up(self):
        self.db = NLP_Database
        
    def test_get_intents_and_expressions(self):
        self.assertEqual(2, 3)