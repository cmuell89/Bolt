"""
Created on Jul 4, 2016

@author: carl
"""
import json
import logging
from database.database import NLPDatabase

logger = logging.getLogger('BOLT.io')


def create_data_for_pipeline_from_file(file_address):
    """
    Function that returns an array of array of training data stored in a JSON file.

    Args:
        file_address: filepath to training data .JSON file
    Returns:
        tuple of lists of training documents and labels
    Raises:
        :IOError Raises IOError if file not found or does not exist.
    """
    try:
        file = open(file_address)
        data = json.load(file)
        intents = data["intents"]
        docs = []
        labels = []
        for intent in intents:
            docs = docs + intent["expressions"]
            for i in range(len(intent["expressions"])):
                labels.append(intent["name"])
        return [docs,labels]
    except IOError as e:
        print("IO error: ", e)


def create_data_for_pipeline_from_database():
    """
    Function that returns an array of array of training data stored in Bolt's postgreSQL database.

    Returns:
        tuple of paired lists of training documents and labels, in that order.
        Returns empty arrays if exception occurs.
    """
    labels = []
    docs = []
    try:
        db = NLPDatabase()
        data = db.get_intents_and_expressions()
        for datum in data:
            labels.append(datum[0])
            docs.append(datum[1])
        return [docs, labels]
    except Exception as e:
        logger.error("Exception occurred importing database data.")
        logger.exception(e)
        logger.debug("returning empty arrays")
        return [docs, labels]


def get_intents_from_JSON_data(fileAddress):
    file_ = open(fileAddress)
    data = json.load(file_)
    intents = data["intents"]
    labels = []
    for intent in intents:
        labels.append(intent["name"])
    return labels
