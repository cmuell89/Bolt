from flask import Flask
from flask import jsonify
from flask_restful import Api
from app import resources
# from werkzeug.exceptions import default_exceptions
# from werkzeug.exceptions import HTTPException

__all__ = ['app']

# def make_json_app(import_name, **kwargs):
#     """
#     Creates a JSON-oriented Flask app.
#     
#     All error responses that you don't specifically
#     manage yourself will have applications/json content
#     type, and will contain JSON like this (just an example)
#     {"message":"405: Method Not Allowed"}
#     
#     Source here: http://flask.pocoo.org/snippets/83/
#     """
#     
#     def make_json_error(ex):
#         response = jsonify(message=str(ex), code=(ex.code if isinstance(ex, HTTPException) else 500))
#         response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
#         return response
#     
#     app = Flask(import_name, **kwargs)
#     
#     for code in default_exceptions:
#         app.error_handler_spec[None][code] = make_json_error
#     return app

app = Flask(__name__)
api = Api(app)

api.add_resource(resources.Classify, '/classification/classify')
api.add_resource(resources.Train, '/classification/train')
