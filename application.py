'''
Created on Jul 18, 2016

@author: carl
'''
import settings
import os
import logging
from app import app as application

logger = logging.getLogger('bolt')

# run the app.
if __name__ == "__main__": 
    if os.environ.get('ENVIRONMENT')=='dev':
        logger.setLevel(logging.DEBUG)
        logger.info("Running in dev mode using eclipse/python interpreter")
        application.run(host=os.environ.get('DEV_HOST'),port=int(os.environ.get('DEV_PORT')), debug=True, use_reloader=True)
    elif os.environ.get('ENVIRONMENT')=='test':
        logger.setLevel(logging.INFO)
        logger.info("Running in test mode using eclipse/python interpreter")
        application.run(debug=True, use_reloader=False)
    elif os.environ.get('ENVIRONMENT')=='prod':
        logger.setLevel(logging.INFO)
        logger.info("Running in production mode...")
        application.run()
