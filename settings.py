from os.path import join, dirname
from dotenv import load_dotenv
import logging
import sys
import os

"""
ENVIRONMENT 
.env settings for local environments
"""


if os.path.isfile(os.path.join(os.path.dirname(__file__), '.env')):
    print("Setting environment variables...")
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
"""
LOGGING
"""
logger = logging.getLogger('BOLT')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)

fileHandler = logging.FileHandler("{0}/{1}.log".format(os.path.join(os.path.dirname(__file__), './logs'), 'stdout'))
fileHandler.setFormatter(formatter)

logger.addHandler(fileHandler)
logger.addHandler(stdoutHandler)

if os.environ.get('ENVIRONMENT') == 'dev':
    logger.setLevel(logging.DEBUG)
    logger.info("Running in development mode. Logging with level DEBUG")
elif os.environ.get('ENVIRONMENT') == 'test':
    logger.setLevel(logging.INFO)
    logger.info("Running in test mode. Logging with level INFO")
elif os.environ.get('ENVIRONMENT') == 'prod':
    logger.setLevel(logging.INFO)
    logger.info("Running in production mode. Logging with level INFO")
