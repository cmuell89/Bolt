'''
Created on Jul 5, 2016

@author: carl
'''

from classification.Classification import buildClassificationPipeline,\
    trainClassificationPipeline, classifyDocument

clf = buildClassificationPipeline()
trained_clf = trainClassificationPipeline(clf)

query = "1"
while(query != "0"):
    query = input("Enter query: ")
    print(classifyDocument(trained_clf,query))


