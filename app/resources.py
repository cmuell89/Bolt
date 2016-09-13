'''
Created on Jul 27, 2016

@author: carl
'''
from flask import jsonify
from flask import request
from flask import Response
from database.database import NLP_Database
from flask_restful import Resource
from classification.classification import train_classification_pipeline, classify_document

"""
Module accessible objects:
    clf: the NLP classification pipeline built using sk-learn (defaults to Naive Bayes 'nb' but can be retrained using Linear SVM 'svm')
    db: the NLP_Database() object used to make calls to the associated Bolt postrgres database
"""
# Defaults to Naive Bayes Classifier
# clf = train_classification_pipeline()
# db = NLP_Database()

class Classify(Resource):
    def post(self):
        """
        Returns the intent classification of the query.
        """
        if request.headers['Content-Type'] == 'application/json':
            result = str(classify_document(clf, request.get_json()['query']))
            resp = jsonify(intent=result)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp
        
class Train(Resource):
    def get(self, classifier):
        """
        Trains the existing classifier object accessed by all '/classification/*' routes.
        """
        if not classifier == 'svm' or classifier == 'nb':
            classifier = 'svm'
        clf = train_classification_pipeline(classifier)
        response_message = "Classifier successfully trained!"
        resp = jsonify(message=response_message)
        resp.status_code = 200
        return resp
    
class Expressions(Resource):
    def post(self, intent):
        """
        Adds expression/s to an intent
        Currently only supports 'application/json' mimetype.
        """
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            try:
                result = db.add_expressions_to_intent(intent, data['expressions'])
                expressions = list(map(lambda tup: tup[0], result)) 
                resp = jsonify(intent=intent,expressions=expressions)
                resp.status_code = 200
                return resp
            except Exception.DatabaseError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 500
                return resp
            except Exception.DatabaseInputError as error:
                resp = jsonify(error=error.value)
                resp.status_code = 400
                return resp
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp
            
    def get(self, intent):
        """
        Returns the expressions for an intent
        """ 
        try:
            result = db.get_intent_expressions(intent)
            expressions = list(map(lambda tup: tup[0], result))
            resp = jsonify(intent=intent,expressions=expressions)
            resp.status_code = 200
            return resp
        except Exception.DatabaseError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 500
            return resp
        except Exception.DatabaseInputError as error:
            resp = jsonify(error=error.value)
            resp.status_code = 400
            return resp
        
    
    def delete(self, intent):
        """
        Deletes an expression/s from an intent
        """
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            if data['all'] == True:
                try:
                    result = db.delete_all_intent_expressions(intent)
                    expressions = list(map(lambda tup: tup[0], result))
                    resp = jsonify(intent=intent,expressions=expressions)
                    return resp
                except Exception.DatabaseError as error:
                    resp = jsonify(error=error.value)
                    resp.status_code = 500
                    return resp
                except Exception.DatabaseInputError as error:
                    resp = jsonify(error=error.value)
                    resp.status_code = 400
                    return resp   
            elif data['expressions']:
                try:
                    result = db.delete_expressions_from_intent(intent, data['expressions'])
                    expressions = list(map(lambda tup: tup[0], result))
                    resp = jsonify(intent=intent,expressions=expressions)
                    return resp
                except Exception.DatabaseError as error:
                    resp = jsonify(error=error.value)
                    resp.status_code = 500
                    return resp
                except Exception.DatabaseInputError as error:
                    resp = jsonify(error=error.value)
                    resp.status_code = 400
                    return resp 
            else:    
                resp = jsonify(error="Missing 'expressions' payload. Please ensure request has an array of string expressions.")
                resp.status_code = 400
                return resp 
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp   
            
class Intents(Resource):
    def post(self):
        """
        Posts an intent to NLP postgres database.
        Currently only supports 'application/json' mimetype.
        """
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            try:
                result = db.add_intent(data['intent'])
                intents = list(map(lambda tup: tup[0], result))
                resp = jsonify(intents=intents)
                resp.status_code = 200
                return resp
            except Exception.DatabaseError as error:
                resp = jsonify(error=error)
                resp.status_code = 500
                return resp
            except Exception.DatabaseInputError as error:
                resp = jsonify(error=error)
                resp.status_code = 400
                return resp
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp
        
    def get(self):
        """
        Gets the current intents stored in the NLP database
        """
        result = db.get_intents()
        intents = list(map(lambda tup: tup[0], result))
        resp = jsonify(intents=intents)
        resp.status_code = 200
        return resp
    
    def delete(self):
        """
        Deletes an intent including all its associated expressions
        """
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            try:
                result = db.delete_intent(data['intent'])
                intents = list(map(lambda tup: tup[0], result))
                resp = jsonify(intents=intents)
                resp.status_code = 200
                return resp
            except Exception.DatabaseError as error:
                resp = jsonify(error=error)
                resp.status_code = 500
                return resp
            except Exception.DatabaseInputError as error:
                resp = jsonify(error=error)
                resp.status_code = 400
                return resp
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp
        
class Health(Resource):
    def get(self):
        """
        Gets the current intents stored in the NLP database
        """
        resp = Response(status_code=200)
        return resp
        
        