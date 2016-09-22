from flask import Flask
from flask import jsonify
from flask_restful import Api
from . import resources
import logging

__all__ = ['application']

application = app = Flask(__name__)

api = Api(app)

api.add_resource(resources.Expressions, '/database/expressions/<string:intent>')
api.add_resource(resources.Intents, '/database/intents')
api.add_resource(resources.Classify, '/classification/classify')
api.add_resource(resources.Train, '/classification/train/<string:classifier>')
api.add_resource(resources.Health, '/aws-eb-health')
