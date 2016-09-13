from os.path import join, dirname
from dotenv import load_dotenv
import logging
import sys
import os


"""
ENVIRONMENT 
.env settings for local environments
"""
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

"""
LOGGING
"""
logger = logging.getLogger('BOLT')

if os.environ.get('ENVIRONMENT')=='dev':
    logger.setLevel(logging.DEBUG)
    stdouth = logging.StreamHandler(sys.stdout)
    stdouth.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdouth.setFormatter(formatter)
    logger.addHandler(stdouth)
    logger.info("Running in development mode. Logging with level DEBUG")
elif os.environ.get('ENVIRONMENT')=='test':
    logger.setLevel(logging.INFO)
    stdouth = logging.StreamHandler(sys.stdout)
    stdouth.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdouth.setFormatter(formatter)
    logger.addHandler(stdouth)
    logger.info("Running in test mode. Logging with level INFO")
elif os.environ.get('ENVIRONMENT')=='prod':
    logger.setLevel(logging.INFO)
    stdouth = logging.StreamHandler(sys.stdout)
    stdouth.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stdouth.setFormatter(formatter)
    logger.addHandler(stdouth)
    logger.info("Running in production mode. Logging with level INFO")
