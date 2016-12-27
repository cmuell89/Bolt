'''
Created on Jul 21, 2016

@author: Carl Mueller

Unit tests for general Bolt module functions, classes and methods. 
'''
import unittest
import sklearn
import settings
import logging
import json
import os
from utils.custom_assertions import CustomAssertions
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor, Classifier
from nlp.ner.gazetteer import GazetteerModelBuilder, GazetteerModelAccessor, Gazetteer
from database.database import ExpressionsDatabaseEngine, IntentsDatabaseEngine
from builtins import int, str

logger = logging.getLogger('BOLT.test')


class EntitiesDatabaseTest(unittest.TestCase, CustomAssertions):

    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: EntitiesDatabaseTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: EntitiesDatabaseTest\n")

    def test_get_intent_entities(self):
        logger.info("TEST: get_intent_entities()")
        db = IntentsDatabaseEngine()
        # entities = db.get_intent_entities('get-best-selling-items')[0][1]
        # self.assertIsInstance(entities, list)
        # self.assertIn('product_name', entities)
        db.release_database_connection()
        self.fail("Test needed.")
        logger.info("TEST PASS: get_intent_entities()")

    def test_add_entities_to_intent(self):
        logger.info("TEST: add_entities_to_intent()")
        db = IntentsDatabaseEngine()
        # db.add_intent('test_intent')
        # test_entities = ['test_entity_one', 'test_entity_two']
        # results = db.add_entities_to_intent('test_intent', test_entities)[0][1]
        # self.assertIn('test_entity_one', results)
        # self.assertIn('test_entity_two', results)
        # second_result = db.add_entities_to_intent('test_intent', 'test_entity_three')[0][1]
        # self.assertIn('test_entity_three', second_result)
        # db.delete_intent('test_intent')
        db.release_database_connection()
        self.fail("Test needed.")
        logger.info("TEST PASS: add_entities_to_intent()")

    def test_delete_entities_from_intent(self):
        logger.info("TEST: delete_entities_from_intent()")
        db = IntentsDatabaseEngine()
        # db.add_intent('test_intent')
        # test_entities = ['test_entity_one', 'test_entity_two', 'test_entity_three']
        # db.add_entities_to_intent('test_intent', test_entities)
        # results = db.delete_entities_from_intent('test_intent', ['test_entity_one', 'test_entity_two'])[0][1]
        # self.assertNotIn('test_entity_one', results)
        # self.assertNotIn('test_entity_two', results)
        # second_results = db.delete_entities_from_intent('test_intent', 'test_entity_three')[0][1]
        # self.assertEqual([], second_results)
        # db.delete_intent('test_intent')
        db.release_database_connection()
        self.fail("Test needed.")
        logger.info("TEST PASS: delete_entities_from_intent()")

    def test_get_entities(self):
        logger.info("TEST: get_entities()")
        self.fail("Test needed.")
        logger.info("TEST PASS: get_entities()")

    def test_add_entity(self):
        logger.info("TEST: add_entities")
        self.fail("Test needed.")
        logger.info("TEST PASS: add_entities()")

    def test_update_entity(self):
        logger.info("TEST: update_entity()")
        self.fail("Test needed.")
        logger.info("TEST PASS: update_entity()")

    def test_delete_entity(self):
        logger.info("TEST: delete_entities_from_intent()")
        self.fail("Test needed.")
        logger.info("TEST PASS: delete_entities_from_intent()")

    def confirm_entity_exists(self):
        logger.info("TEST: delete_entities_from_intent()")
        self.fail("Test needed.")
        logger.info("TEST PASS: delete_entities_from_intent()")

class StopwordsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """

    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUTIE: EntitiesDatabaseTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: EntitiesDatabaseTest\n")

    def test_get_intent_stopwords(self):
        logger.info("TEST START: get_intent_stopwords()")
        db = IntentsDatabaseEngine()
        stopwords = db.get_intent_stopwords('get-best-selling-items')[0][1]
        self.assertIsInstance(stopwords, list)
        self.assertIn('selling', stopwords)
        db.release_database_connection()
        logger.info("TEST PASS: get_intent_stopwords()")

    def test_add_stopwords_to_intent(self):
        logger.info("TEST: add_entities_to_stopwords()")
        db = IntentsDatabaseEngine()
        db.add_intent('test_intent')
        test_stopwords = ['stop_one', 'stop_two']
        results = db.add_stopwords_to_intent('test_intent', test_stopwords)[0][1]
        self.assertIn('stop_one', results)
        self.assertIn('stop_one', results)
        second_result = db.add_stopwords_to_intent('test_intent', 'stop_three')[0][1]
        self.assertIn('stop_three', second_result)
        db.delete_intent('test_intent')
        db.release_database_connection()
        logger.info("TEST PASS: add_stopwords_to_stopwords()")

    def test_delete_stopwords_from_intent(self):
        logger.info("TEST: delete_stopwords_from_intent()")
        db = IntentsDatabaseEngine()
        db.add_intent('test_intent')
        test_stopwords = ['stop_one', 'stop_two', 'stop_three']
        db.add_stopwords_to_intent('test_intent', test_stopwords)
        results = db.delete_stopwords_from_intent('test_intent', ['stop_one', 'stop_two'])[0][1]
        self.assertNotIn('stop_one', results)
        self.assertNotIn('stop_two', results)
        second_results = db.delete_stopwords_from_intent('test_intent', 'stop_three')[0][1]
        self.assertEqual([], second_results)
        db.delete_intent('test_intent')
        db.release_database_connection()
        logger.info("TEST PASS: delete_stopwords_from_intent()")


class IntentsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: IntentsDatabaseTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: IntentsDatabaseTest\n")

    def test_get_intents(self):
        logger.debug("TEST: get_intents()")
        db = IntentsDatabaseEngine()
        intents = db.get_intents()
        self.assertListOfString(intents)
        db.release_database_connection()
        logger.info("TEST PASS: get_intents()")

    def test_add_intent(self):
        logger.debug("TEST: add_intent()")
        db = IntentsDatabaseEngine()
        new_list_of_intents = db.add_intent('some-new-intent')
        self.assertIn('some-new-intent', new_list_of_intents)
        db.delete_intent('some-new-intent')
        db.release_database_connection()
        logger.info("TEST PASS: add_intent()")

    def test_delete_intent(self):
        logger.debug("TEST: delete_intent()")
        db = IntentsDatabaseEngine()
        db.add_intent('soon-to-be-deleted')
        results = db.delete_intent('soon-to-be-deleted')
        self.assertNotIn(('soon-to-be-deleted',), results)
        logger.info("TEST PASS: delete_intent()")

    def test_confirm_intent_exists(self):
        logger.debug("TEST: confirm_intent_exists()")
        db = IntentsDatabaseEngine()
        db.add_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(True, intent_exists)
        db.delete_intent('confirmation-intent')
        intent_exists = db.confirm_intent_exists('confirmation-intent')
        self.assertEqual(False, intent_exists)
        logger.info("TEST PASS: confirm_intent_exists()")


class ExpressionsDatabaseTest(unittest.TestCase, CustomAssertions):
    """
    Class for unit testing all methods with the database.database.NLP_Database class
    """
    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: ExpresssionsDatabaseTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: ExpresssionsDatabaseTest\n")

    '''
    Retrieval operations.
    '''
    def test_get_intents_and_expressions(self):
        logger.debug("TEST: get_intents_and_expressions()")
        db = ExpressionsDatabaseEngine()
        intents_and_expressions = db.get_intents_and_expressions()
        self.assertListOfTuples(intents_and_expressions, [str, str])
        db.release_database_connection()
        logger.info("TEST PASS: get_intents_and_expressions()")

    def test_get_intent_expressions(self):
        logger.debug("TEST: get_intent_expressions()")
        db = ExpressionsDatabaseEngine()
        intent_expressions = db.get_intent_expressions('get-order')
        self.assertListOfString(intent_expressions)
        db.release_database_connection()
        logger.info("TEST PASS: get_intent_expressions()")

    def test_get_unlabeled_expressions(self):
        logger.debug("TEST: get_unlabeled_expressions()")
        db = ExpressionsDatabaseEngine()
        unlabeled_expressions = db.get_unlabeled_expressions()
        self.assertListOfTuples(unlabeled_expressions, [int, str, str, float])
        db.release_database_connection()
        logger.info("TEST PASS: get_unlabeled_expressions()")

    def test_get_unlabeled_expression_by_id(self):
        logger.debug("TEST: get_unlabeled_expression_by_id()")
        db = ExpressionsDatabaseEngine()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        tuple_list = [tup for tup in results if tup[1] == 'This is an unlabeled expression']
        actual_unlabeled_expression = tuple_list[0]
        test_unlabeled_expression = db.get_unlabeled_expression_by_id(actual_unlabeled_expression[0])
        self.assertEqual(actual_unlabeled_expression, test_unlabeled_expression)
        db.release_database_connection()
        logger.info("TEST PASS: get_unlabeled_expression_by_id()")

    def test_get_archived_expressions(self):
        logger.debug("TEST: get_archived_epxressions()")
        db = ExpressionsDatabaseEngine()
        unlabeled_expressions = db.get_archived_expressions()
        self.assertListOfTuples(unlabeled_expressions, [int, str, str, float])
        db.release_database_connection()
        logger.info("TEST PASS: get_archived_epxressions()")

    '''
    Addition operations
    '''
    def test_add_expressions_to_intent(self):
        logger.debug("TEST: add_expressions_to_intent()")
        expressions_db = ExpressionsDatabaseEngine()
        intents_db = IntentsDatabaseEngine()
        intents_db.add_intent('expressionless')
        # Test for a list of expressions as argument.
        obj = expressions_db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], obj)
        # Test for a string as argument.
        obj2 = expressions_db.add_expressions_to_intent('expressionless', "Expression argument is a string")
        self.assertListOfString(obj)
        self.assertListEqual(["Expression one", "Expression two", "Expression three", "Expression argument is a string"], obj2)
        intents_db.delete_intent('expressionless')
        expressions_db.release_database_connection()
        intents_db.release_database_connection()
        logger.info("TEST PASS: add_expressions_to_intent()")

    def test_add_unlabeled_expression(self):
        logger.debug("TEST: add_unlabeled_expression()")
        db = ExpressionsDatabaseEngine()
        results = db.add_unlabeled_expression('This is an unlabeled expression', 'guess-intent', .9900)
        self.assertListOfTuples(results, [int, str, str, float])
        expression_id = [tup[0] for tup in results if tup[1] == 'This is an unlabeled expression']
        db.delete_unlabeled_expression_by_id(expression_id[0])
        db.release_database_connection()
        logger.info("TEST PASS: add_unlabeled_expression()")

    def test_add_archived_expressions(self):
        logger.debug("TEST: add_archived_expressions()")
        db = ExpressionsDatabaseEngine()
        results = db.add_archived_expression('This is an archived expression', 'guess-intent', .9900)
        self.assertListOfTuples(results, [int, str, str, float])
        expression_id = [tup[0] for tup in results if tup[1] == 'This is an archived expression']
        db.delete_archived_expression_by_id(expression_id[0])
        db.release_database_connection()
        logger.info("TEST PASS: add_archived_expressions()")

    '''
    Deletion operations.
    '''
    def test_delete_expressions_from_intent(self):
        logger.debug("TEST: delete_expressions_from_intent()")
        expressions_db = ExpressionsDatabaseEngine()
        intents_db = IntentsDatabaseEngine()
        intents_db.add_intent('expressionless')
        expressions_db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        obj = expressions_db.delete_all_intent_expressions('expressionless')
        self.assertEqual(len(obj), 0)
        intents_db.delete_intent('expressionless')
        expressions_db.release_database_connection()
        intents_db.release_database_connection()
        logger.info("TEST PASS: delete_expressions_from_intent()")

    def test_delete_unlabeled_expression(self):
        logger.debug("TEST: delete_unlabeled_expressions()")
        test_expression = 'This is another unlabeled expression'
        db = ExpressionsDatabaseEngine()
        before_results = db.add_unlabeled_expression(test_expression, 'guess-intent', .9900)
        before_expression = [tup[1] for tup in before_results]
        self.assertIn(test_expression, before_expression)
        expression_id = [tup[0] for tup in before_results if tup[1] == test_expression]
        after_results = db.delete_unlabeled_expression_by_id(expression_id[0])
        after_expression = [tup[1] for tup in after_results]
        self.assertNotIn((test_expression,), after_expression)
        logger.info("TEST PASS: delete_unlabeled_expressions()")

    def test_delete_archived_expression(self):
        logger.debug("TEST: delete_archived_expresssion()")
        test_expression = 'This is another archived expression'
        db = ExpressionsDatabaseEngine()
        before_results = db.add_archived_expression(test_expression, 'guess-intent', .9900)
        before_expression = [tup[1] for tup in before_results]
        self.assertIn(test_expression, before_expression)
        expression_id = [tup[0] for tup in before_results if tup[1] == test_expression]
        after_results = db.delete_archived_expression_by_id(expression_id[0])
        after_expression = [tup[1] for tup in after_results]
        self.assertNotIn((test_expression,), after_expression)
        logger.info("TEST PASS: delete_archived_expresssion()")

    '''
    Confirmation operations
    '''
    def test_confirm_unlabeled_expression_exists(self):
        logger.debug("TEST: confirm_unlabeled_expression_exists()")
        test_expression = 'This is another unlabeled expression'
        db = ExpressionsDatabaseEngine()
        results = db.add_unlabeled_expression(test_expression, 'guess-intent', .9900)
        expression_id = [tup[0] for tup in results if tup[1] == test_expression]
        expression_exists = db.confirm_unlabeled_expression_exists(expression_id[0])
        self.assertEqual(True, expression_exists)
        db.delete_unlabeled_expression_by_id(expression_id[0])
        expression_exists = db.confirm_unlabeled_expression_exists(expression_id[0])
        self.assertEqual(False, expression_exists)
        logger.info("TEST PASS: confirm_unlabeled_expression_exists()")

    def test_confirm_archived_expression_exists(self):
        logger.debug("TEST: confirm_archived_expression_exists()")
        test_expression = 'This is another archived expression'
        db = ExpressionsDatabaseEngine()
        results = db.add_archived_expression(test_expression, 'guess-intent', .9900)
        expression_id = [tup[0] for tup in results if tup[1] == test_expression]
        expression_exists = db.confirm_archived_expression_exists(expression_id[0])
        self.assertEqual(True, expression_exists)
        db.delete_archived_expression_by_id(expression_id[0])
        expression_exists = db.confirm_archived_expression_exists(expression_id[0])
        self.assertEqual(False, expression_exists)
        logger.info("TEST PASS: confirm_archived_expression_exists()")


class ClassifierTest(unittest.TestCase):
    """
    Class for unit testing all methods with the nlp.clf.classification.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: ClasiifierTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE: ClasiifierTest\n")

    def test_tokenize_text(self):
        logger.debug("TEST: _tokenize_text()")
        builder = ClassificationModelBuilder()
        test = builder._tokenize_text("What is the best selling item of  all  time?")
        actual = [u"what", u"be", u"the", u"best", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
        logger.info("TEST PASS: _tokenize_text()")

    def test_build_classification_pipeline(self):
        logger.debug("TEST: build_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._build_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: build_classification_pipeline")

    def test_train_classification_pipeline(self):
        logger.debug("TEST: _train_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._train_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: _train_classification_pipeline")

    def test_classify(self):
        logger.debug("TEST: classify()")
        builder = ClassificationModelBuilder()
        accesor = ClassificationModelAccessor()
        builder.update_serialized_model()
        clf = accesor.get_classification_pipeline('intent_classifier')
        self.assertEqual(Classifier, type(clf))
        result = clf.classify("What is the best selling item of all time?")
        self.assertIsInstance(result, dict)
        self.assertEqual("get-best-selling-items", result['intents'][0]['intent'])
        logger.info("TEST PASS: classify()")


class GazetteerTest(unittest.TestCase):
    """
    Class for unit testing all methods with the nlp.ner.gazetteer.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: GazetteerTest")

    @classmethod
    def tearDownClass(cls):
        logger.info("TEST SUITE PASS: GazetteerTest\n")

    def test_create_new_gazetteer_model(self):
        logger.debug("TEST: create_new_gazetteer_model()")
        with open(os.path.join(os.path.dirname(__file__), '../resources/entities_for_testing.json')) as file_:
            json_data = json.load(file_)
            entities = json_data['test_entities']
            builder = GazetteerModelBuilder()
            accessor = GazetteerModelAccessor()
            builder.create_new_gazetteer_model('example_type', 'test-key', entities)
            gazetteers = accessor.get_gazeteers('test-key')
            test_gazetteer = gazetteers['example_type']
            self.assertIsInstance(test_gazetteer, Gazetteer)
            results = test_gazetteer.search_query('entity1')
            self.assertEqual('entity1', results)
        logger.info("TEST PASS: create_new_gazetteer_model()")

    def test_update_single_gazetteer_model(self):
        logger.debug("TEST: create_new_gazetteer_model()")
        with open(os.path.join(os.path.dirname(__file__), '../resources/entities_for_testing.json')) as file_:
            json_data = json.load(file_)
            entities = json_data['test_entities']
            update_entities = json_data['test_update_entities']
            builder = GazetteerModelBuilder()
            accessor = GazetteerModelAccessor()
            builder.create_new_gazetteer_model('example_type', 'test-key', entities)
            builder.update_single_gazetteer_model('example_type', 'test-key', update_entities)
            gazetteers = accessor.get_gazeteers('test-key')
            test_gazetteer = gazetteers['example_type']
            self.assertIsInstance(test_gazetteer, Gazetteer)
            results = test_gazetteer.search_query('entity5')
            self.assertEqual('entity5', results)
        logger.info("TEST PASS: create_new_gazetteer_model()")
