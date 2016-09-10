'''
Created on Jul 27, 2016

@author: carl
'''
import unittest
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('./test')
    unittest.TextTestRunner(verbosity=1).run(testsuite)