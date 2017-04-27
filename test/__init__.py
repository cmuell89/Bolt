from unittest import TestSuite
from test.test_app import NLPTest, ExpressionsTest, IntentsTest, UnlabeledExpressionsTest, ArchivedExpressionsTest
from test.test_general import ClassifierTest, EntitiesDatabaseTest, StopwordsDatabaseTest, IntentsDatabaseTest, \
                              ExpressionsDatabaseTest, GazetteerTest
import settings

test_cases = (NLPTest, ExpressionsTest, IntentsTest, UnlabeledExpressionsTest, ArchivedExpressionsTest, ClassifierTest,
              EntitiesDatabaseTest, StopwordsDatabaseTest, IntentsDatabaseTest, ExpressionsDatabaseTest, GazetteerTest)

def load_tests(loader, tests, pattern):
    suite = TestSuite()
    for test_class in test_cases:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    return suite