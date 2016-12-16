"""
Created on December 5, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""

import json
import string
import sys
from nltk.corpus import stopwords
from sklearn import naive_bayes
from sklearn import svm
from sklearn.base import TransformerMixin
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.feature_selection import chi2, SelectKBest
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.pipeline import Pipeline, FeatureUnion
from spacy.en import English
import pickle
import numpy as np
import timeit
import re

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
    classes = data["classes"]
    docs = []
    labels = []
    for cls in classes:
        docs = docs + cls["expressions"]
        for i in range(len(cls["expressions"])):
            labels.append(cls["label"])
    return [docs, labels]


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

def regexCallable(regex_list):
    for pattern in self.regex_list:
        results = []
        regex = re.compile(pattern)
        result = regex.search(query)
        if result is not None:
            match = result.group(0)
            results.append(match)
    return results


"""
DATA
    - Extract training data from intents.json and include a set of test data.
"""
data = createTrainingDataFromJSON("../resources/is_plural.json");

trainingData = data[0]
labeledData = data[1]

"""
SETUP
    - the vectorizer, feature selector, and classifier definitions
    - different parameters to be used by GridSearch model selector
    - note that I changed the tokenizer in CountVectorizer to use a custom function using spaCy's tokenizer
    - CountVectorizer is ski_learn native class API to create feature vectosrs. In this case word frequency and bigrams.


    NOTE: look into DictVectorizer to create new features and scipy.sparse.hstack to stack sparse feature matrices.
"""
# regex_vectorizer = CountVectorizer(analyzer=regexCallable[r"('s)"])
vocabulary_vectorizer = CountVectorizer(vocabulary=["items","products"])
ngram_vectorizer = CountVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=1)
vectorizer = CountVectorizer(tokenizer=tokenizeText, ngram_range=(1, 2))
combined_vectorizer = FeatureUnion([("ngram", ngram_vectorizer), ("token", vectorizer), ("vocab", vocabulary_vectorizer)])
tfidf = TfidfTransformer(norm='l2', use_idf=True)
lsvc_clf = svm.LinearSVC()

# the final to clean, tokenize, vectorize, feature select and classifier determined by GridSearchCV above
clf = CalibratedClassifierCV(lsvc_clf)
pipe = Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', combined_vectorizer), ('tfidf', tfidf), ('clf', clf)])

################################################################################################################
# train
pipe.fit(trainingData, labeledData)
classes = pipe.classes_.tolist()

# test
string = 'some string'
while (string):
    query = input('Enter query: ')
    query = cleanText(query)
    classification_result = pipe.predict([query])
    class_probabilities = pipe.predict_proba([query]).tolist()
    confidence_metrics = list(zip(classes, class_probabilities[0]))
    results = sorted(confidence_metrics, key=lambda tup: tup[1], reverse=True)
    print()
    for i in range(0, 2):
        print(results[i])
    print()