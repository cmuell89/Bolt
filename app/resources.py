'''
Created on Jul 27, 2016

@author: Carl Mueller

clf: the NLP classification pipeline built using sk-learn (defaults to Naive Bayes 'svm' but can be retrained using Linear SVM 'svm')
db: the NLP_Database() object used to make calls to the associated Bolt postgreSQL database

'''
import logging
import re
from flask import jsonify, request, Response, abort
from flask_restful import Resource
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser
from marshmallow import Schema, fields
from .authorization import auth
from .validators import valid_application_type, list_of_strings
from functools import partial
from database.database import NLP_Database
from classification.classification import train_classification_pipeline, classify_document
from utils.exceptions import DatabaseError, DatabaseInputError

logger = logging.getLogger('BOLT.api')

try:
    clf = train_classification_pipeline()
    logger.info('Created default LinearSVC classifier on startup')
except Exception as e:
    logger.exception(e)
    logger.warning("All API endpoints requiring the trained clf will fail.")
    
try:
    db = NLP_Database()
except Exception as e:
    logger.exception(e)
    logger.warning("All API endpoints requiring a db connection will fail.")

"""
Resources Classes
"""
class Classify(Resource):
    
    decorators = [auth.login_required]
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
        resp = jsonify(intents=result)
        resp.status_code = 200
        return resp
        
        
class Train(Resource):
    
    decorators = [auth.login_required]
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
    
    decorators = [auth.login_required]
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
            result = db.add_expressions_to_intent(intent, args['expressions'])
            expressions = list(map(lambda tup: tup[0], result)) 
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
            result = db.get_intent_expressions(intent)
            expressions = list(map(lambda tup: tup[0], result))
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
                result = db.delete_all_intent_expressions(intent)
                expressions = list(map(lambda tup: tup[0], result))
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
                result = db.delete_expressions_from_intent(intent, args['expressions'])
                expressions = list(map(lambda tup: tup[0], result))
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

     
class Intents(Resource):
    
    decorators = [auth.login_required]
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
            result = db.add_intent(args['intent'])
            intents = list(map(lambda tup: tup[0], result))
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
        result = db.get_intents()
        intents = list(map(lambda tup: tup[0], result))
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
            result = db.delete_intent(args['intent'])
            intents = list(map(lambda tup: tup[0], result))
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
        