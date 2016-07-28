from unittest import TestSuite
from test.test_app import Classification_Test, Expressions_Test
from test.test_general import Classifier_Test, NLP_Database_Test


test_cases = (Classification_Test, Expressions_Test, Classifier_Test, NLP_Database_Test)

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite