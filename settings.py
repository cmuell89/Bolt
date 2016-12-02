from os.path import join, dirname
from dotenv import load_dotenv
import logging.handlers
import sys
import os

"""
ENVIRONMENT 
.env settings for local environments
"""
if os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

"""
LOGGING
"""
application_logger = logging.getLogger('BOLT')
werkzeug_logger = logging.getLogger('werkzeug')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)
application_logger.addHandler(stdoutHandler)
werkzeug_logger.addHandler(stdoutHandler)

if os.environ.get('ENVIRONMENT') == 'dev':
    fileHandler = logging.FileHandler("{0}/{1}.log".format(os.path.join(os.path.dirname(__file__), './logs'), 'stdout'))
    fileHandler.setFormatter(formatter)
    application_logger.addHandler(fileHandler)

paperTrailsHandler = logging.handlers.SysLogHandler(address=(os.environ.get('PAPERTRAILS_ADDRESS')
                                                             , int(os.environ.get('PAPERTRAILS_PORT'))))
paperTrailsHandler.setFormatter(formatter)
application_logger.addHandler(paperTrailsHandler)
werkzeug_logger.addHandler(paperTrailsHandler)

if os.environ.get('ENVIRONMENT') == 'dev':
    application_logger.setLevel(logging.DEBUG)
    werkzeug_logger.setLevel(logging.DEBUG)
    application_logger.info("Running in development mode. Logging with level DEBUG")
elif os.environ.get('ENVIRONMENT') == 'test':
    application_logger.setLevel(logging.INFO)
    werkzeug_logger.setLevel(logging.INFO)
    application_logger.info("Running in test mode. Logging with level INFO")
elif os.environ.get('ENVIRONMENT') == 'prod':
    application_logger.setLevel(logging.INFO)
    werkzeug_logger.setLevel(logging.INFO)
    application_logger.info("Running in production mode. Logging with level INFO")
