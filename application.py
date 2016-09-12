'''
Created on Jul 18, 2016

@author: carl
'''
import os
import logging
from app import app as application
from os.path import join, dirname
from dotenv import load_dotenv

'''
Loads environment variables.
'''
dotenv_path = join(dirname(__file__), '.env')
if os.path.isfile(dotenv_path) == True:
    load_dotenv(dotenv_path)
logger = logging.getLogger('bolt')
 
if os.environ.get('ENVIRONMENT')=='dev':
    logger.setLevel(logging.DEBUG)
    logger.info("Running in dev mode using eclipse/python interpreter")
    application.run(host=os.environ.get('HOST'), debug=True, use_reloader=True)
elif os.environ.get('ENVIRONMENT')=='test':
    logger.setLevel(logging.INFO)
    logger.info("Running in test mode using eclipse/python interpreter")
    application.run(host=os.environ.get('HOST'), port=os.environ.get('PORT'), debug=False, use_reloader=False)
elif os.environ.get('ENVIRONMENT'=='prod'):
    logger.setLevel(logging.INFO)
    logger.info("Running in production mode...")
    application.run()
