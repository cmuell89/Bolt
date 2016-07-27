'''
Created on Jul 18, 2016

@author: carl
'''
from app import app
from flask import request
from flask import jsonify
from flask import Response
from classification.Classification import train_classification_pipeline, classify_document

clf = train_classification_pipeline()

@app.route('/test', methods = ['GET'])
def test():
    return u'Test response'

@app.route('/classification/classify', methods = ['POST'])
def classify():
    """
    Returns the intent classification of the query.
    
    Requires mimetype to be application/json. Support for other content types might expand in the future.
    JSON data in the request must include a 'query' key.
    """
    if request.headers['Content-Type'] == 'application/json':
        result = str(classify_document(clf, request.get_json()['query']))
        resp = jsonify(intent=result)
        resp.status_code = 200
        return resp
    else:
        return unsupported_content_type()    

@app.route('/classification/train', methods = ['GET'])
def train():
    """
    Trains the existing classifier object accessed by all '/classification/*' routes.
    """
    clf = train_classification_pipeline()
    resp = Response()
    resp.status_code = 200
    return resp

@app.errorhandler(415)
def unsupported_content_type(error=None):
    message = {
            'status': 415,
            'message': 'Unsupported media type: ' + str(request.headers),
    }
    resp = jsonify(message)
    resp.status_code = 415

    return resp