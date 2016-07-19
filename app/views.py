'''
Created on Jul 18, 2016

@author: carl
'''
from app import app
from flask import request
import json

from classification.Classification import trainClassificationPipeline, classifyDocument

clf = trainClassificationPipeline()

@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"

@app.route('/classification', methods = ['POST'])
def classify():
    data = request.get_json(silent=True)
    return str(classifyDocument(clf, data['query']))