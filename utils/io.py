'''
Created on Jul 4, 2016

@author: carl
'''
import json


# Function that returns an array of array of training data. First array are documents, second array is the labels.
def createTrainingDataFromJSON(fileAddress):
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