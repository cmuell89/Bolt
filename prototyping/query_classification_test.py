'''
Created on Jul 5, 2016

@author: carl
'''

from classification.classification import build_classification_pipeline, train_classification_pipeline, classify_document

clf = build_classification_pipeline()
trained_clf = train_classification_pipeline(clf)

query = "1"
while(query != "0"):
    query = input("Enter query: ")
    print(classify_document(trained_clf,query))


