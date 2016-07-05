'''
Created on Jul 4, 2016

@author: Carl Mueller
'''
from flask import Flask


app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'