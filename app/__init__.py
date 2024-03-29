from flask import Flask, g
from flask_restful import Api
from utils.sslify import SSLify
from .resources import restful_api, web_client
import logging
import os

logger = logging.getLogger('BOLT.app')

__all__ = ['application']

application = app = Flask(__name__)

""" SSL """
if(os.environ.get("ENVIRONMENT") == 'prod' or os.environ.get("ENVIRONMENT") == 'test'):
    sslify = SSLify(app, permanent=True, skips=['aws-eb-health'], no_redirects=['nlp', 'database'])

application.secret_key = os.environ.get('SECRET_KEY')

@app.teardown_appcontext
def close_connection(exception):
    logger.debug('Tearing down app context')
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
api.add_resource(restful_api.Train, '/nlp/train')
api.add_resource(restful_api.Health, '/aws-eb-health')


