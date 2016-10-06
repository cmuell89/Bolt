'''
Created on Jul 27, 2016

@tokenAuthor: Carl Mueller

clf: the NLP classification pipeline built using sk-learn (defaults to Naive Bayes 'svm' but can be retrained using Linear SVM 'svm')
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
from database.database import NLPDatabase
from classification.classification import train_classification_pipeline, classify_document
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.api')

try:
    clf = train_classification_pipeline()
    logger.info('Created default LinearSVC classifier on startup')
except Exception as e:
    logger.exception(e)
    logger.warning("All API endpoints requiring the trained clf will fail.")

"""
Store database object and its connections in the local context object g.
"""    

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = db = NLPDatabase()
    return db

"""
Resources Classes
"""
class Classify(Resource):
    
    decorators = [tokenAuth.login_required]
    validate_application_json = partial(valid_application_type, 'application/json')
    
    classify_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
        'query': fields.Str(required=True, validate=validate.Length(min=1))
    }
    
    @use_args(classify_args)
    def post(self, args):
        """
        Returns the intent classification of the query.
        """
        result = classify_document(clf, args['query'])
        intent_guess = result[0]['intent']
        estimated_confidence = result[0]['confidence']
        try:
            db = get_db()
            db.add_unlabeled_expression(args['query'], intent_guess, estimated_confidence)
        except DatabaseError as e:
            logger.exception(e.value)
        resp = jsonify(intents=result)
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
        if classifier not in ('svm','nb'):
            classifier = 'svm'
            response_message = "Classifier defaulting to " + classifier + " due to malformed variable URL."
        else:
            response_message = "Classifier successfully trained: " + classifier
        clf = train_classification_pipeline(None,None, classifier)
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
            db = get_db()
            expressions = db.add_expressions_to_intent(intent, args['expressions'])
            resp = jsonify(intent=intent,expressions=expressions)
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
            db = get_db()
            expressions = db.get_intent_expressions(intent)
            resp = jsonify(intent=intent,expressions=expressions)
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
                db = get_db()
                expressions = db.delete_all_intent_expressions(intent)
                resp = jsonify(intent=intent,expressions=expressions)
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
                db = get_db()
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
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_application_json),
    }

    @use_args(unlabeled_get_args)
    def get(self, args):
        """
        Gets as list of tuples of unlabeled expressions.
        """
        try:
            db = get_db()
            unlabeled_expressions = db.get_unlabeled_expressions()
            resp = jsonify(unlabeled_expressions = unlabeled_expressions)
            resp.status_code = 200
            return resp
        except DatabaseError as errror:
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
            db = get_db()
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
        db = get_db()
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
            db = get_db()
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
        