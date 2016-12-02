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
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)
paperTrailsHandler = logging.handlers.SysLogHandler(address=(os.environ.get('PAPERTRAILS_ADDRESS')
                                                             , int(os.environ.get('PAPERTRAILS_PORT'))))
paperTrailsHandler.setFormatter(formatter)

application_logger = logging.getLogger('BOLT')
application_logger.addHandler(stdoutHandler)
application_logger.addHandler(paperTrailsHandler)


if os.environ.get('ENVIRONMENT') == 'dev':
    """ Only used for development purposes since werkzeug server is replaced by Apache and mod_wsgi in production """
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(stdoutHandler)
    werkzeug_logger.addHandler(paperTrailsHandler)
    werkzeug_logger.setLevel(logging.INFO)
    application_logger.setLevel(logging.DEBUG)
    application_logger.info("Running in development mode. Logging with level DEBUG")
elif os.environ.get('ENVIRONMENT') == 'test':
    application_logger.setLevel(logging.INFO)
    application_logger.info("Running in test mode. Logging with level INFO")
elif os.environ.get('ENVIRONMENT') == 'prod':
    application_logger.setLevel(logging.INFO)
    application_logger.info("Running in production mode. Logging with level INFO")
