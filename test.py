'''
Created on Jul 27, 2016

@author: carl
'''
import unittest
import logging
from os.path import join, dirname
from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
            
if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('./test')
    unittest.TextTestRunner(verbosity=1).run(testsuite)