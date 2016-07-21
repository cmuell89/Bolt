'''
Created on Jul 4, 2016

@author: carl
'''
import json


# Function that returns an array of array of training data. First array are documents, second array is the labels.
def create_data_for_pipeline(fileAddress):
    file = open(fileAddress)
    data = json.load(file)
    intents = data["intents"]
    docs = []
    labels = []
    for intent in intents:
        docs = docs + intent["expressions"]
        for i in range(len(intent["expressions"])):
            labels.append(intent["name"])
    return [docs,labels]

def get_intents_from_JSON_data(fileAddress):
    file = open(fileAddress)
    data = json.load(file)
    intents = data["intents"]
    labels = []
    for intent in intents:
        labels.append(intent["name"])
    return labels