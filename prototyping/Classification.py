'''
Created on May 28, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
'''


import json
import string

from nltk.corpus import stopwords
# from sklearn import naive_bayes
from sklearn import svm
from sklearn.base import TransformerMixin
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline
from spacy.en import English

import numpy as np

# A custom stoplist
STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "ca"] + list(ENGLISH_STOP_WORDS))
# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]

# create parser    
parser = English()


# Every step in a pipeline needs to be a "transformer". 
# Define a custom transformer to clean text using spaCy
class CleanTextTransformer(TransformerMixin):
    """
    Convert text to cleaned text
    """

    def transform(self, X, **transform_params):
        return [cleanText(text) for text in X]

    def fit(self, X, y=None, **fit_params):
        return self

    def get_params(self, deep=True):
        return {}

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

# A custom function to clean the text before sending it into the vectorizer
def cleanText(text):
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")
    
    # lowercase, perhaps not a good thing for proper nouns?
    text = text.lower()
    
    return text

# A custom function to tokenize the text using spaCy
# and convert to lemmas
def tokenizeText(sample):
    
    # get the tokens using spaCy
    tokens = parser(sample)
        
    # lemmatize
    lemmas = []
    for tok in tokens:
        lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    tokens = lemmas
    
    # stoplist the tokens
    # tokens = [tok for tok in tokens if tok not in STOPLIST]

    # stoplist symbols
    tokens = [tok for tok in tokens if tok not in SYMBOLS]

    # remove large strings of whitespace
    while "" in tokens:
        tokens.remove("")
    while " " in tokens:
        tokens.remove(" ")
    while "\n" in tokens:
        tokens.remove("\n")
    while "\n\n" in tokens:
        tokens.remove("\n\n")

    return tokens

def printNMostInformative(vectorizer, clf, N):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names()
    coefs_with_fns = sorted(zip(clf.coef_[0], feature_names))
    topClass1 = coefs_with_fns[:N]
    topClass2 = coefs_with_fns[:-(N + 1):-1]
    print("Class 1 best: ")
    for feat in topClass1:
        print(feat)
    print("Class 2 best: ")
    for feat in topClass2:
        print(feat)

# May only work with LinearSVC() classifier.
def print_top10(vectorizer, clf, class_labels):
    """Prints features with the highest coefficient values, per class"""
    feature_names = vectorizer.get_feature_names()
    print(feature_names)
    for i, class_label in enumerate(class_labels):
        top10 = np.argsort(clf.coef_[i])[-10:]
        print("%s:" % (class_label))
        print(" ".join((feature_names[j]) for j in top10),)
        print()
    
# the vectorizer and classifer to use
# note that I changed the tokenizer in CountVectorizer to use a custom function using spaCy's tokenizer
# CountVectorizer is ski_learn native class API to create feature vectosrs. In this case word frequency and bigrams.
vectorizer = CountVectorizer(tokenizer=tokenizeText, ngram_range=(1,2))
clf = svm.LinearSVC()
#clf = naive_bayes.MultinomialNB()
# the pipeline to clean, tokenize, vectorize, and classify
pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer), ('clf', clf)])

# Extract training data from intents.json
trainingData = createTrainingDataFromJSON("./intents.json");
train = trainingData[0]
labelsTrain = trainingData[1]


test = ["What are the best selling items this quarter?", "How many customers did I in California this year?", "What items are on sale?",
        "What are my best selling kyle flannel?", "best selling items of all time", "Get me order 3213?", "How many new customers last weekend?",
        "Get me the last 10 orders","get me all refunded orders from today", "list the refunded orders from this month.", "Show me all the one sale items today.",
        "Who is my top customer?", "Who was my top customer this month?", "What is my best selling SM3?", "get me order 2132"]
labelsTest = ["get-best-selling-items", "get-customer-count-by-state", "get-on-sale-items",
              "get-best-selling-items","get-best-selling-items","get-order","get-new-customer-count",
              "get-most-recent-order","get-refunded-orders", "get-refunded-orders", "get-on-sale-items",
              "get-top-customers","get-top-customers","get-best-selling-items","get-order"]

################################################################################################################
# train
pipe.fit(train, labelsTrain)

# test
string = 'some string'
while(string):
    query = input('Enter query: ')
    query = cleanText(query)
    print(pipe.predict([query]))
    print()
    
preds = pipe.predict(test)
print("----------------------------------------------------------------------------------------------")
print("results:")
for (sample, pred) in zip(test, preds):
    print(sample, ":", pred)
print("accuracy:", accuracy_score(labelsTest, preds))

print("----------------------------------------------------------------------------------------------")
print("Top 10 features used to predict: ")
# show the top features
# printNMostInformative(vectorizer, clf, 10)
print_top10(vectorizer, clf, clf.classes_)

print("----------------------------------------------------------------------------------------------")
print("The original data as it appeared to the classifier after tokenizing, lemmatizing, stoplisting, etc")
# let's see what the pipeline was transforming the data into
pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer)])
transform = pipe.fit_transform(train, labelsTrain)

# get the features that the vectorizer learned (its vocabulary)
vocab = vectorizer.get_feature_names()

# the values from the vectorizer transformed data (each item is a row,column index with value as # times occurring in the sample, stored as a sparse matrix)
# for i in range(len(train)):
#     s = ""
#     indexIntoVocab = transform.indices[transform.indptr[i]:transform.indptr[i+1]]
#     numOccurences = transform.data[transform.indptr[i]:transform.indptr[i+1]]
#     for idx, num in zip(indexIntoVocab, numOccurences):
#         s += str((vocab[idx], num))
#     print("Sample {}: {}".format(i, s))