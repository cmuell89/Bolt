import os
from flask_httpauth import HTTPTokenAuth, HTTPBasicAuth


basicAuth = HTTPBasicAuth()
tokenAuth = HTTPTokenAuth(scheme='Token')

users = ["carl", "dylan"]

@tokenAuth.verify_token
def verify_token(token):
    if token == os.environ.get('ACCESS_TOKEN'):
        return True
    return False

@basicAuth.get_password
def get_pw(username):
    if username in users:
        return os.environ.get('ACCESS_TOKEN')
    return None