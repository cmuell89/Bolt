'''
Created on Jul 27, 2016

@tokenAuthor: Carl Mueller

__CLF__: the NLP classification pipeline built using sk-learn (defaults to Naive Bayes 'svm' but can be retrained using Linear SVM 'svm')
db: the NLP_Database() object used to make calls to the associated Bolt postgreSQL database

Classes:
    Analyze:
        post - Returns the intent classification of the query, and the entities and stopwords of the intent.
    Train:
        get - Trains the existing classifier object accessed by all '/classification/*' routes.
    Expressions:
        get - Returns the expressions for an intent
        post - Adds expression/s to an intent. Returns the update list of expressions for the intent.
        delete - Deletes expression/s from intent. Returns the update list of expressions for the intent.
    UnlabeledExpressions:
        get - Returns as list of tuples of unlabeled expressions.
    Intents:
        get - Returns the current intents stored in the NLP database
        post - Posts an intent to NLP postgres database. Returns current list of intents.
        delete- Deletes intent and all expressions associated with that intent (SHOULD MIGRATE EXPRESSIONS INTO UNLABELED EXPRESSION.  Returns current list of intents.
    Health:
        get - Used by AWS Elastic Beanstalk service to monitor health. Returns 200.
'''
import logging
from flask import jsonify, Response, abort, g
from flask_restful import Resource
from webargs import validate
from webargs.flaskparser import use_args, parser
from marshmallow import fields
from functools import partial
from app.authorization import tokenAuth
from app.validators import valid_application_type, list_of_strings
from database.database import IntentsDatabaseEngine, ExpressionsDatabaseEngine
from nlp import Analyzer, Updater
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.api')


def get_db(database):
    """
    Store database objects and its connections in the local context object g.
    :param database:
    :return: The referenced database object given the type.
    """
    db = getattr(g, '_database', None)
    if db is None:
        intents_db = IntentsDatabaseEngine()
        expressions_db = ExpressionsDatabaseEngine()
        database_dict = {'intents': intents_db,
              'expressions': expressions_db}
        g._database = db = database_dict
    return db[database]


class Analyze(Resource):

    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    analyze_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'query': fields.Str(required=True, validate=validate.Length(min=1)),
        'key': fields.Str(required=True, validate=validate.Length(min=1))
    }
    
    @use_args(analyze_args)
    def post(self, args):
        """
        POST route that returns the analysis on a given query (classification results, entities etc,.)
        :param args: Incoming data from request containing the query and the access key.
        :return: JSON response with the results of the Analyzer on the query
        """
        analyzer = Analyzer()
        results = analyzer.run_analysis(args['query'], args['key'])
        estimated_intent = results['classification'][0]['intent']
        estimated_confidence = results['classification'][0]['confidence']
        try:
            db = get_db('expressions')
            db.add_unlabeled_expression(args['query'], estimated_intent, estimated_confidence)
        except DatabaseError as e:
            logger.exception(e.value)
        resp = jsonify(results)
        resp.status_code = 200
        return resp
        
        
class Train(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    train_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json)
    }
    
    @use_args(train_args)
    def get(self, args, classifier):
        """
        Trains the existing classification models used by Classifier objects.
        :param classifier: Classifier type (nb, svm)
        :return:
        """
        if classifier not in ('svm', 'nb'):
            classifier = 'svm'
            response_message = "Classifier defaulting to " + classifier + " due to malformed variable URL."
        else:
            response_message = "Classifier successfully trained: " + classifier
        updater = Updater()
        updater.update_classifier(classifier)
        resp = jsonify(message=response_message)
        resp.status_code = 200
        return resp


class Expressions(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    expressions_post_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'expressions': fields.List(fields.Str(), required=True, validate=list_of_strings)
    }
    
    @use_args(expressions_post_args)
    def post(self, args, intent):
        """
        Adds expression/s to an intent
        Currently only supports 'application/json' mimetype.
        :param args: dict containing expressions argument.
        :param intent: Target intent that is passed in as a URL query parameter.
        :return:
        """
        try:
            db = get_db('expressions')
            expressions = db.add_expressions_to_intent(intent, args['expressions'])
            resp = jsonify(intent=intent, expressions=expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
        
    expressions_get_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json)
    }

    @use_args(expressions_get_args)
    def get(self, args, intent):
        """
        Retrieves the the expressions for an intent
        :param intent: Target intent that is passed in as a URL query parameter.
        :return: JSON containing the itnent name and list of expressions for that intent
        """

        try:
            db = get_db('expressions')
            expressions = db.get_intent_expressions(intent)
            resp = jsonify(intent=intent, expressions=expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp

    expressions_delete_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'expressions': fields.List(fields.Str(), required=True, validate=list_of_strings),
        'all': fields.Bool(missing=False, validate=lambda val: isinstance(val, bool))
    }
    
    @use_args(expressions_delete_args)
    def delete(self, args, intent):
        """
        Deletes expressions from a given intent
        :param args: Dict containg 'expressions': The expressions to be deleted; 'all': boolean value that determines if
                     all expressiosn are deleted.
        :param intent: Target intent that is passed in as a URL query parameter.
        :return: If 'all' returns dict with intent and empty expressions list, else dict of intent with new list of
                 expressions
        """
        if args['all'] == True:
            try:
                db = get_db('expressions')
                expressions = db.delete_all_intent_expressions(intent)
                resp = jsonify(intent=intent, expressions=expressions)
                return resp
            except DatabaseError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 500
                return resp
            except DatabaseInputError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 400
                return resp   
        elif args['expressions']:
            try:
                db = get_db('expressions')
                expressions = db.delete_expressions_from_intent(intent, args['expressions'])
                resp = jsonify(intent=intent,expressions=expressions, deleted_expressions=args['expressions'])
                return resp
            except DatabaseError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 500
                return resp
            except DatabaseInputError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 400
                return resp 


class UnlabeledExpressions(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')

    unlabeled_get_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json)
    }

    @use_args(unlabeled_get_args)
    def get(self, args):
        """
        :return: Returns a JSON styled list of the unlabeled expressions
        """
        try:
            db = get_db('expressions')
            unlabeled_expressions = list(map(lambda x: {"id": x[0],
                                                        "expression": x[1],
                                                        "estimated_intent": x[2],
                                                        "estimated_confidence": x[3]},
                                             db.get_unlabeled_expressions()))
            resp = jsonify(unlabeled_expressions=unlabeled_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
    
    unlabeled_post_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'expression': fields.Str(required=True),
        'estimated_intent': fields.Str(required=False),
        'estimated_confidence': fields.Int(required=False)
    }
    
    @use_args(unlabeled_post_args)
    def post(self, args):
        """
        Adds an unlabeled_expression to database including additional data
        :param args: arg[expression]: expression to add to unlabeled list in database
                     args[estimated_intent]: guess intent from classifier
                     args[estimated_confidence]: classifier's confidence on the guess intent
        :return: Returns a JSON styled list of the unlabeled expressions
        """
        """
        Adds an unlabeled expression to database.
        """
        try:
            db = get_db('expressions')
            db_results = db.add_unlabeled_expression(args['expression'], args['estimated_intent'], args['estimated_confidence'])
            unlabeled_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db_results))
            resp = jsonify(unlabeled_expressions=unlabeled_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
    
    unlabeled_delete_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'id': fields.Int(required=True)
    }

    @use_args(unlabeled_delete_args)
    def delete(self, args):
        """
        :param args: args['id']: id of unlabeled expression to be deleted
        :return: JSON styled list of unlabeled_expressions
        """
        try:
            db = get_db('expressions')
            db_results = db.delete_unlabeled_expression_by_id(args['id'])
            unlabeled_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db_results))
            resp = jsonify(unlabeled_expressions=unlabeled_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp


class ArchivedExpressions(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')

    archived_get_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json)
    }

    @use_args(archived_get_args)
    def get(self, args):
        """
        :return: Returns JSON styled list of archived expressions
        """
        try:
            db = get_db('expressions')
            archived_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db.get_archived_expressions()))
            resp = jsonify(archived_expressions=archived_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
    
    archived_post_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'expression': fields.Str(required=True),
        'estimated_intent': fields.Str(required=True),
        'estimated_confidence': fields.Float(required=True)
    }
    
    @use_args(archived_post_args)
    def post(self, args):
        """
        Adds archived expression to database.
        :param args: arg[expression]: expression to add to archived expressions list in database
                     args[estimated_intent]: guess intent from classifier
                     args[estimated_confidence]: classifier's confidence on the guess intent
        :return: Returns a JSON styled list of the archived expressions
        """
        try:
            db = get_db('expressions')
            db_results = db.add_archived_expression(args['expression'], args['estimated_intent'], args['estimated_confidence'])
            archived_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db_results))
            resp = jsonify(archived_expressions=archived_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
    
    archived_delete_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'id': fields.Int(required=True)
    }
    
    @use_args(archived_delete_args)
    def delete(self, args):
        """
        :param args: args['id']: id of archived expression to be deleted
        :return: JSON styled list of archived_expressions
        """
        try:
            db = get_db('expressions')
            db_results = db.delete_archived_expression_by_id(args['id'])
            archived_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db_results))
            resp = jsonify(archived_expressions = archived_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp


class Intents(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    intents_post_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'intent': fields.Str(required=True, validate=lambda val: len(val) > 0),
        'entities': fields.List(fields.Str(), required=False),
        'stopwords': fields.List(fields.Str(), required=False)
    }
    
    @use_args(intents_post_args)
    def post(self, args):
        """
        Posts an intent to NLP postgres database.
        Currently only supports 'application/json' mimetype.
        :param args: args['intent']: name of intent to be added
                     args['entities']: list of entities associated with intent
                     args['stopwords']: list of custom stopwords associated with intent and its expressions
        :return: JSON styled list of intents
        """
        """

        """
        try:
            db = get_db('intents')
            db.add_intent(args['intent'])
            if args['entities']:
                db.add_entities_to_intent(args['intent'], args['entities'])
            if args['stopwords']:
                db.add_stopwords_to_intent(args['intent'], args['stopwords'])
            intents = db.get_intents()
            resp = jsonify(intents=intents)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
    
    intents_get_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
    }
    
    @use_args(intents_get_args)
    def get(self, args):
        """
        :return: JSON styled list of intents in database.
        """
        db = get_db('intents')
        intents = db.get_intents()
        resp = jsonify(intents=intents)
        resp.status_code = 200
        return resp

    intents_delete_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'intent': fields.Str(required=True, validate=lambda val: len(val) > 0)
    }
    
    @use_args(intents_delete_args)
    def delete(self, args):
        """
        Deletes an intent including all its associated expressions
        :param args: args['intent']: Intent to be deleted
        :return: JSON styled list of intents less the deleted intent
        """
        try:
            db = get_db('intents')
            intents = db.delete_intent(args['intent'])
            resp = jsonify(intents=intents)
            resp.status_code = 200
            return resp
        except DatabaseError as error:
            resp = jsonify(error=error)
            resp.status_code = 500
            return resp
        except DatabaseInputError as error:
            resp = jsonify(error=error)
            resp.status_code = 400
            return resp


class Health(Resource):

    def get(self):
        """
        Health endpoint used by AWS elastic beanstalk to determine the load/stress on current deployment.
        :return: 200 response.
        """
        resp = Response()
        return resp


@parser.error_handler
def handle_request_parsing_error(err):
    """
    webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    :param err: err object
    """

    code, msg = getattr(err, 'status_code', 400), getattr(err, 'messages', 'Invalid Request')
    abort(code, msg)
