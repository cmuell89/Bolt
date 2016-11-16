'''
Created on Oct 3, 2016

@author: Carl Mueller


Web client endpoints.
Class: ValidateExpression - Contains post method for to handle form data coming from the validate unlabeled expression page.

'''
import logging
from functools import partial
from flask import request, Response, redirect, g, render_template, flash, url_for
from flask.views import MethodView
from webargs import validate
from webargs.flaskparser import use_args
from marshmallow import fields
from app.authorization import basicAuth
from app.validators import valid_application_type
from database.database import IntentsDatabaseEngine, EntitiesDatabaseEngine, StopwordDatabaseEngine, ExpressionsDatabaseEngine
from flask.templating import render_template

logger = logging.getLogger('BOLT.api')

"""
Store database object and its connections in the local context object g.
"""    

def get_db(database):
    """

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


class Home(MethodView):
    
    decorators = [basicAuth.login_required]

    def get(self):
        db = get_db('expressions')
        unlabeled_expressions = db.get_unlabeled_expressions()
        return render_template('index.html', expressions=unlabeled_expressions)


class ValidateExpression(MethodView):
    
    decorators = [basicAuth.login_required]
    validate_urlencoded = partial(valid_application_type, 'application/x-www-form-urlencoded')
    validation_args = {
        'content_type': fields.Str(required=True, load_from='Content-Type', location='headers', validate=validate_urlencoded),
        'id': fields.Int(required=True),
        'expression': fields.Str(required=True),
        'intent': fields.Str(required=True),
        "gridRadios": fields.Str(required=True)
    }
    
    '''
    Try Catch statements needed.
    '''
    @use_args(validation_args)
    def post(self, args):
        expressions_db = get_db('expressions')
        intents_db = get_db('intents')
        if args['gridRadios'] == 'validate':
            logger.debug("Validating expression '{0}' for intent '{1}'".format(args['expression'], args['intent']))
            if intents_db.confirm_intent_exists(args['intent']):
                expressions_db.add_expressions_to_intent(args['intent'], args['expression'])
                expressions_db.delete_unlabeled_expression(args['id'])
                return redirect(url_for('home'))
            else:
                logger.debug("Intent '{0}' does not exist".format(args['intent']))
                flash('Could not find that intent! Make sure it exists prior to adding an expression.')
                return redirect(url_for('home'))
        elif args['gridRadios'] == 'archive':
            logger.debug("Archiving expression '{0}' for intent '{1}'".format(args['expression'], args['intent']))
            expression = expressions_db.get_unlabeled_expression_by_id(args['id'])
            estimated_intent = expression[2]
            estimated_confidence = expression[3]
            expressions_db.add_archived_expression(args['expression'], estimated_intent, estimated_confidence)
            expressions_db.delete_unlabeled_expression(args['id'])
            return redirect(url_for('home'))
        elif args['gridRadios'] == 'delete':
            logger.debug("Deleting expression '{0}' from unlabeled expressions table".format(args['expression'], args['intent']))
            expressions_db.delete_unlabeled_expression(args['id'])
            return redirect(url_for('home'))
