from flask import Flask
from flask import jsonify
from flask_restful import Api
from app import resources
import logging

__all__ = ['application']

application = app = Flask(__name__)

application.debug=True
# # run the app.
# if __name__ == "__main__":
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production app.
# #     application.debug = True
#     application.run()

api = Api(app)

api.add_resource(resources.Expressions, '/database/expressions/<string:intent>')
api.add_resource(resources.Intents, '/database/intents')
api.add_resource(resources.Classify, '/classification/classify')
api.add_resource(resources.Train, '/classification/train/<string:classifier>')
api.add_resource(resources.Health, '/aws-eb-health')
