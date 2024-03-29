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
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor, IntentClassifier, BinaryClassifier
from nlp.ner.gazetteer import GazetteerModelBuilder, GazetteerModelAccessor, Gazetteer
from database.database import ExpressionsDatabaseEngine, IntentsDatabaseEngine, EntitiesDatabaseEngine
from builtins import int, str

logger = logging.getLogger('BOLT.test')


class EntitiesDatabaseTest(unittest.TestCase, CustomAssertions):

    @classmethod
    def setUpClass(cls):
        cls.entities_db = EntitiesDatabaseEngine()
        cls.intents_db = IntentsDatabaseEngine()
        cls.intents_db.add_intent('test_intent')
        cls.entities_db.add_entity('test_entity', 'test_type', ['reg1', 'reg2'], ['key1', 'key2'])
        logger.info("TEST SUITE: EntitiesDatabaseTest")

    @classmethod
    def tearDownClass(cls):
        cls.entities_db.delete_entity('test_entity')
        cls.intents_db.delete_intent('test_intent')
        cls.entities_db.release_database_connection()
        cls.intents_db.release_database_connection()
        logger.info("TEST SUITE PASS: EntitiesDatabaseTest\n")

    def test_get_intent_entities(self):
        logger.info("TEST: get_intent_entities()")
        db = IntentsDatabaseEngine()
        results = db.get_intent_entities('get_best_selling_items')
        self.assertListOfTuples(results, [int, str, str, list, list])
        entities = []
        for result in results:
            entities.append(result[1])
        self.assertIn('product_name', entities)
        db.release_database_connection()
        logger.info("TEST PASS: get_intent_entities()")

    def test_add_entities_to_intent(self):
        logger.info("TEST: add_entities_to_intent()")
        intents_db = IntentsDatabaseEngine()
        entities_db = EntitiesDatabaseEngine()
        entities_db.confirm_entity_exists('test_entity')
        results = intents_db.add_entities_to_intent('test_intent', ['test_entity'])
        self.assertListOfTuples(results, [int, str, str, list, list])
        entities = []
        for result in results:
            entities.append(result[1])
        self.assertIn('test_entity', entities)
        intents_db.delete_entities_from_intent('test_intent', ['test_entity'])
        intents_db.release_database_connection()
        entities_db.release_database_connection()
        logger.info("TEST PASS: add_entities_to_intent()")

    def test_delete_entities_from_intent(self):
        logger.info("TEST: delete_entities_from_intent()")
        intents_db = IntentsDatabaseEngine()
        entities_db = EntitiesDatabaseEngine()
        entities_db.confirm_entity_exists('test_entity')
        results = intents_db.add_entities_to_intent('test_intent', ['test_entity'])
        self.assertListOfTuples(results, [int, str, str, list, list])
        results = intents_db.delete_entities_from_intent('test_intent', ['test_entity'])
        entities = []
        for result in results:
            entities.append(result[1])
        self.assertNotIn('test_entity', entities)
        intents_db.release_database_connection()
        entities_db.release_database_connection()
        logger.info("TEST PASS: delete_entities_from_intent()")

    def test_get_entities(self):
        logger.info("TEST: get_entities()")
        db = EntitiesDatabaseEngine()
        results = db.get_entities()
        self.assertListOfTuples(results, [int, str, str, list, list])
        entities = []
        for result in results:
            entities.append(result[1])
        self.assertIn('test_entity', entities)
        for result in results:
            if result[1] == 'test_entity':
                self.assertEqual(result[2], 'test_type')
                self.assertEqual(result[3], ['reg1', 'reg2'])
                self.assertEqual(result[4], ['key1', 'key2'])
        db.release_database_connection()
        logger.info("TEST PASS: get_entities()")

    def test_get_entity(self):
        logger.info("TEST: get_entity()")
        db = EntitiesDatabaseEngine()
        result = db.get_entity('test_entity')
        entity = result[0]
        self.assertEqual(entity[1], 'test_entity')
        self.assertEqual(entity[2], 'test_type')
        self.assertEqual(entity[3], ['reg1', 'reg2'])
        self.assertEqual(entity[4], ['key1', 'key2'])
        db.release_database_connection()
        logger.info("TEST PASS: get_entity()")

    def test_add_entity(self):
        logger.info("TEST: add_entity")
        db = EntitiesDatabaseEngine()
        results = db.add_entity('second_test_entity', 'test_type', ['reg1', 'reg2'], ['key1', 'key2'])
        self.assertListOfTuples(results, [int, str, str, list, list])
        entities = [result[1] for result in results]
        self.assertIn('second_test_entity', entities)
        for result in results:
            if result[1] == 'second_test_entity':
                self.assertEqual(result[2], 'test_type')
                self.assertEqual(result[3], ['reg1', 'reg2'])
                self.assertEqual(result[4], ['key1', 'key2'])
        db.delete_entity('second_test_entity')
        db.release_database_connection()
        logger.info("TEST PASS: add_entities()")

    def test_update_entity(self):
        logger.info("TEST: update_entity()")
        db = EntitiesDatabaseEngine()
        updates = {'entity_name': 'updated_name', 'entity_type': 'updated_type',
                   'regular_expressions': ['reg1', 'reg2', 'reg3'], 'keywords': ['key1', 'key2', 'key3']}
        db.add_entity('second_test_entity', 'test_type', ['reg1', 'reg2'],
                      ['key1', 'key2'])
        result = db.update_entity('second_test_entity', **updates)[0]
        self.assertEqual(result[1], 'updated_name')
        self.assertEqual(result[2], 'updated_type')
        self.assertEqual(result[3], ['reg1', 'reg2', 'reg3'])
        self.assertEqual(result[4], ['key1', 'key2', 'key3'])
        db.delete_entity('updated_name')
        db.release_database_connection()
        logger.info("TEST PASS: update_entity()")

    def test_delete_entity(self):
        logger.info("TEST: delete_entity()")
        db = EntitiesDatabaseEngine()
        results = db.add_entity('second_test_entity', 'test_type', ['reg1', 'reg2'],
                                ['key1', 'key2'])
        entities = [result[1] for result in results]
        self.assertIn('second_test_entity', entities)
        results = db.delete_entity('second_test_entity')
        entities = [result[1] for result in results]
        self.assertNotIn('second_test_entity', entities)
        db.release_database_connection()
        logger.info("TEST PASS: delete_entity()")

    def test_confirm_entity_exists(self):
        logger.info("TEST: confirm_entity_exists()")
        db = EntitiesDatabaseEngine()
        self.assertTrue(db.confirm_entity_exists('test_entity'))
        db.release_database_connection()
        logger.info("TEST PASS: confirm_entity_exists()")

    def test_get_binary_entity_expressions(self):
        logger.info("TEST: get_binary_entity_expressions()")
        db = EntitiesDatabaseEngine()
        db_results = db.get_binary_entity_expressions("is_plural")
        self.assertListOfTuples(db_results, [int, str, bool])
        db.release_database_connection()
        logger.info("TEST PASS: get_binary_entity_expressions()")

    def test_add_binary_entity_to_expression(self):
        logger.info("TEST: add_binary_entity_to_expression()")
        expressions_db = ExpressionsDatabaseEngine()
        intent_expressions = expressions_db.add_expressions_to_intent('test_intent', ['test_expression'])
        expression_id = intent_expressions[0][0]
        entities_db = EntitiesDatabaseEngine()
        results = entities_db.add_binary_entity_to_expression(expression_id, 'test_entity', True)
        expression_entry = list(filter(lambda x: (x[0] == expression_id), results))
        self.assertEqual('test_expression', expression_entry[0][1])
        self.assertEqual(True, expression_entry[0][2])
        entities_db.delete_binary_entity_from_expression(expression_id, 'test_entity')
        entities_db.release_database_connection()
        expressions_db.release_database_connection()
        logger.info("TEST PASS: add_binary_entity_to_expression()")

    def test_delete_binary_entity_from_expression(self):
        logger.info("TEST: delete_binary_entity_from_expression()")
        expressions_db = ExpressionsDatabaseEngine()
        intent_expressions = expressions_db.add_expressions_to_intent('test_intent', 'test_expression')
        expression_id = intent_expressions[0][0]
        entities_db = EntitiesDatabaseEngine()
        entities_db.add_binary_entity_to_expression(expression_id, 'test_entity', True)
        results = entities_db.delete_binary_entity_from_expression(expression_id, 'test_entity')
        expressions = []
        for result in results:
            expressions.append(result[1])
        self.assertNotIn('text_expression', expressions)
        entities_db.release_database_connection()
        expressions_db.release_database_connection()
        logger.info("TEST PASS: delete_binary_entity_from_expression()")


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
        stopwords = db.get_intent_stopwords('get_best_selling_items')[0][1]
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
        db.release_database_connection()
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
        db.release_database_connection()
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
        intent_expressions = db.get_intent_expressions('get_order')
        self.assertListOfTuples(intent_expressions, [int, str])
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
        results = expressions_db.add_expressions_to_intent('expressionless', ["Expression one", "Expression two", "Expression three"])
        self.assertListOfTuples(results, [int, str])
        expressions = [x[1] for x in results]
        self.assertListEqual(["Expression one", "Expression two", "Expression three"], expressions)
        # Test for a string as argument.
        results = expressions_db.add_expressions_to_intent('expressionless', "Expression argument is a string")
        self.assertListOfTuples(results, [int, str])
        expressions = [x[1] for x in results]
        self.assertListEqual(["Expression one", "Expression two", "Expression three", "Expression argument is a string"], expressions)
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
        db.release_database_connection()
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
        db.release_database_connection()
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
        db.release_database_connection()
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
        db.release_database_connection()
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
        actual = [u"what", u"be", u"the", u"good", u"sell", u"item", u"of", u"all", u"time"]
        self.assertListEqual(test, actual)
        logger.info("TEST PASS: _tokenize_text()")

    def test_build_binary_classification_pipeline(self):
        logger.debug("TEST: build_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._build_binary_classification_pipeline(['key1', 'key2'])
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: build_classification_pipeline")

    def test_build_intent_classification_pipeline(self):
        logger.debug("TEST: build_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._build_intent_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: build_classification_pipeline")

    def test_train_binary_classification_pipeline(self):
        logger.debug("TEST: _train_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._build_binary_classification_pipeline(['key1, key2'])
        pipeline = builder._train_binary_classification_pipeline(pipeline,
                                                                 ['pos1', 'pos2', 'pos3', 'neg1', 'neg2', 'neg3'],
                                                                 ['true', 'true', 'true', 'false', 'false', 'false'])
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: _train_classification_pipeline")

    def test_train_intent_classification_pipeline(self):
        logger.debug("TEST: _train_classification_pipeline")
        builder = ClassificationModelBuilder()
        pipeline = builder._train_intent_classification_pipeline()
        self.assertIsInstance(pipeline, sklearn.pipeline.Pipeline)
        logger.info("TEST PASS: _train_classification_pipeline")

    def test_classify(self):
        logger.debug("TEST: classify()")
        builder = ClassificationModelBuilder()
        accesor = ClassificationModelAccessor()
        builder.initialize_classification_models()
        """ multiclass """
        clf = accesor.get_classification_pipeline('multiclass', 'intent_classifier')
        self.assertEqual(IntentClassifier, type(clf))
        result = clf.classify("What is the best selling item of all time?")
        self.assertIsInstance(result, dict)
        self.assertEqual("get_best_selling_items", result['intents'][0]['intent'])
        """ binary_classifier """
        clf = accesor.get_classification_pipeline('binary_classifier', 'is_plural')
        self.assertEqual(BinaryClassifier, type(clf))
        result = clf.classify("Who were my top customers?")
        self.assertEqual("true", result[0][0])
        logger.info("TEST PASS: classify()")


class GazetteerTest(unittest.TestCase):
    """
    Class for unit testing all methods with the nlp.ner.gazetteer.
    """

    @classmethod
    def setUpClass(cls):
        logger.info("TEST SUITE: GazetteerTest")
        cls.key = '8b10af10-011b-11e6-896c-6924b93e8186'

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
            builder.create_new_gazetteer_model('product_name', GazetteerTest.key, entities)
            gazetteers = accessor.get_gazeteers(GazetteerTest.key)
            test_gazetteer = gazetteers['product_name']
            self.assertIsInstance(test_gazetteer, Gazetteer)
        logger.info("TEST PASS: create_new_gazetteer_model()")

    def test_gazetteer_model_by_key(self):
        logger.debug("TEST: create_new_gazetteer_model()")
        with open(os.path.join(os.path.dirname(__file__), '../resources/entities_for_testing.json')) as file_:
            json_data = json.load(file_)
            entities = json_data['test_entities']
            builder = GazetteerModelBuilder()
            accessor = GazetteerModelAccessor()
            builder.create_new_gazetteer_model('product_name', GazetteerTest.key, entities)
            builder.update_gazetteer_models_by_key(GazetteerTest.key)
            gazetteers = accessor.get_gazeteers(GazetteerTest.key)
            test_gazetteer = gazetteers['product_name']
            self.assertIsInstance(test_gazetteer, Gazetteer)
        logger.info("TEST PASS: create_new_gazetteer_model()")
