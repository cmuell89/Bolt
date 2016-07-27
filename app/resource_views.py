'''
Created on Jul 27, 2016

@author: carl
'''
from flask import jsonify
from flask import request
from flask_restful import Resource
from classification.Classification import train_classification_pipeline, classify_document

clf = train_classification_pipeline()

class Test(Resource):
    def get(self):
        response_message = "Test response"
        resp = jsonify(message=response_message)
        resp.status_code = 200
        return resp

class Classify(Resource):
    def post(self):
        """
        Returns the intent classification of the query.
        """
        result = str(classify_document(clf, request.get_json()['query']))
        resp = jsonify(intent=result)
        resp.status_code = 200
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