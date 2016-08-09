'''
Created on Jul 27, 2016

@author: carl
'''
from flask import jsonify
from flask import request
from database.database import NLP_Database
from flask_restful import Resource
from classification.Classification import train_classification_pipeline, classify_document

"""
Module accessible objects:
    clf: the NLP classification pipeline built using sk-learn
    db: the NLP_Database() object used to make calls to the associated Bolt postrgres database
"""
clf = train_classification_pipeline()
db = NLP_Database()

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
    def get(self):
        """
        Trains the existing classifier object accessed by all '/classification/*' routes.
        """
        clf = train_classification_pipeline()
        response_message = "Classifier successfully trained!"
        resp = jsonify(message=response_message)
        resp.status_code = 200
        return resp
    
class Expressions(Resource):
    def post(self, intent):
        """
        Adds expression/s to an intent
        """
        if request.headers['Content-Type'] == 'application/json':
            data = request.get_json()
            result = db.add_expressions_to_intent(intent, data['expressions']) 
            expressions = [];
            for res in result:
                expressions.append(res[0])
            resp = jsonify(intent=intent,expressions=expressions)
            resp.status_code = 200
            return resp
        else:
            resp = jsonify(message="Unsupported media type. Currently the API only accepts 'application/json'.")
            resp.status_code = 415
            return resp
            
    def get(self, intent):
        """
        Returns the expressions for an intent
        """ 
        result = db.get_intent_expressions(intent)
        expressions = []
        for res in result:
            expressions.append(res[0])
        resp = jsonify(intent=intent,expressions=expressions)
        resp.status_code = 200
        return resp

class Intents(Resource):
    def post(self):
        """
        Adds an intent to postgres
        """
        data = request.get_json()
        result = db.add_intent(data['intent'])
        resp = jsonify(result)
        
        
        
        
        