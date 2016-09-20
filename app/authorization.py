import os
from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Token')

@auth.verify_token
def verify_token(token):
    if token == os.environ.get('ACCESS_TOKEN'):
        return True
    return False