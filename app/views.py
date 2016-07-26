'''
Created on Jul 18, 2016

@author: carl
'''
from app import app
from flask import request

from classification.Classification import train_classification_pipeline, classify_document

clf = train_classification_pipeline()

@app.route('/test', methods = ['GET'])
def test():
    return u'Test response'


@app.route('/classification/classify', methods = ['POST'])
def classify():
    data = request.get_json(silent=True)
    return str(classify_document(clf, data['query']))
