'''
Created on Jul 18, 2016

@author: carl
'''
import os
from app import app
from os.path import join, dirname
from dotenv import load_dotenv

'''
Loads environment variables.
'''
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

if __name__ == "__main__":
    if os.environ.get('ENVIRONMENT')=='dev':
        app.run(host=os.environ.get('HOST'),port=os.environ.get('PORT'), debug=True, use_reloader=False)
    else:
        app.run()
