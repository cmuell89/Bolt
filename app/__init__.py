from flask import Flask, jsonify, g
from flask_restful import Api
from .resources import restful_api, web_client
import logging

__all__ = ['application']

application = app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        for key, db_class_instance in db.items():
            db_class_instance.release_database_connection()
"""
Web client routes.
"""
app.add_url_rule('/', view_func=web_client.Home.as_view('default'))
app.add_url_rule('/home', view_func=web_client.Home.as_view('home'))
app.add_url_rule('/validation', view_func=web_client.ValidateExpression.as_view('validation'))

"""
API routes.
"""
api = Api(app)
api.add_resource(restful_api.Expressions, '/database/expressions/<string:intent>')
api.add_resource(restful_api.Intents, '/database/intents')
api.add_resource(restful_api.UnlabeledExpressions, '/database/unlabeled_expressions')
api.add_resource(restful_api.ArchivedExpressions, '/database/archived_expressions')
api.add_resource(restful_api.Analyze, '/nlp/analyze')
api.add_resource(restful_api.Train, '/classification/train/<string:classifier>')
api.add_resource(restful_api.Health, '/aws-eb-health')
