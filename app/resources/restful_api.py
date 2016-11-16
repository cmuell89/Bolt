'''
Created on Jul 27, 2016

@tokenAuthor: Carl Mueller

__CLF__: the NLP classification pipeline built using sk-learn (defaults to Naive Bayes 'svm' but can be retrained using Linear SVM 'svm')
db: the NLP_Database() object used to make calls to the associated Bolt postgreSQL database

Classes:
    Classify:
        post - Returns the intent classification of the query.
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
from database.database import IntentsDatabaseEngine, ExpressionsDatabaseEngine, EntitiesDatabaseEngine, StopwordDatabaseEngine
from nlp import Analyzer, Updater
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.api')


# TODO Refactor with new analyzer

def get_db(database):
    """
    Store database objects and its connections in the local context object g.
    :param database:
    :return: The referenced database object given the type.
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = {'intents': IntentsDatabaseEngine(),
              'expressions': ExpressionsDatabaseEngine(),
              'stopwords': StopwordDatabaseEngine(),
              'entites': EntitiesDatabaseEngine()}
        db = g._database = db
    return db[database]


class Analyze(Resource):

    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    analyze_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'query': fields.Str(required=True, validate=validate.Length(min=1)),
        'id': fields.Str(required=True, validate=validate.Length(min=1))
    }
    
    @use_args(analyze_args)
    def post(self, args):
        """
        Returns the intent classification of the query.
        """
        analyzer = Analyzer()
        results = analyzer.run_analysis(args['query'], args['id'])
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
        Trains the existing classifier object accessed by all '/classification/*' routes.
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
        Returns the expressions for an intent
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
        Deletes an expression/s from an intent
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
        Gets a list of tuples of unlabeled expressions.
        """
        try:
            db = get_db('expressions')
            unlabeled_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db.get_unlabeled_expressions()))
            resp = jsonify(unlabeled_expressions = unlabeled_expressions)
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
        Deleted an unlabeled expression from the database by ID.
        """
        try:
            db = get_db('expressions')
            db_results = db.delete_unlabeled_expression(args['id'])
            unlabeled_expressions = list(map(lambda x: {"id": x[0], "expression": x[1], "estimated_intent": x[2], "estimated_confidence":x[3]}, db_results))
            resp = jsonify(unlabeled_expressions = unlabeled_expressions)
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
        Gets as list of tuples of archived expressions.
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
        Deletes an archived expressions from database based on ID.
        """
        try:
            db = get_db('expressions')
            db_results = db.delete_archived_expression(args['id'])
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
        'intent': fields.Str(required=True, validate=lambda val: len(val) > 0)
    }
    
    @use_args(intents_post_args)
    def post(self, args):
        """
        Posts an intent to NLP postgres database.
        Currently only supports 'application/json' mimetype.
        """
        try:
            db = get_db('intents')
            intents = db.add_intent(args['intent'])
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
        Gets the current intents stored in the NLP database
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
        Gets the current intents stored in the NLP database
        """
        resp = Response()
        return resp


@parser.error_handler
def handle_request_parsing_error(err):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    code, msg = getattr(err, 'status_code', 400), getattr(err, 'messages', 'Invalid Request')
    abort(code, msg)
