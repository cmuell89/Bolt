from unittest import TestSuite
from test.test_app import ClassificationTest, ExpressionsTest, IntentsTest
from test.test_general import ClassifierTest, NLPDatabaseTest
import settings

test_cases = (ClassificationTest, NLPDatabaseTest, ExpressionsTest, IntentsTest, ClassifierTest)

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite