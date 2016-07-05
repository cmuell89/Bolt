'''
Created on May 28, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
'''

import string

from nltk.corpus import stopwords
from sklearn import svm
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from textacy.preprocess import normalize_whitespace

from models.spacy_model import load_spacy_pipeline
from transformers.CleanTextTransformer import CleanTextTransformer
from utils import io


# from sklearn import naive_bayes
# load Spacy pipeline from cached model    
nlp = load_spacy_pipeline

# A custom stoplist
STOPLIST = set(stopwords.words('english') + ["n't", "'s", "'m", "ca"] + list(ENGLISH_STOP_WORDS))
# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]

# A custom function to tokenize the text using spaCy
# and convert to lemmas (may be useful only for classificaiton 
# but not other types of functionality (traits like plurality etc,.)
def tokenizeText(sample):
    
    # get the tokens using spaCy
    tokens = nlp(sample)
        
    # lemmatize
    lemmas = []
    for tok in tokens:
        lemmas.append(tok.lemma_.lower().strip() if tok.lemma_ != "-PRON-" else tok.lower_)
    tokens = lemmas
    
    # stoplist the tokens (seems to worsen model performance, likely because our training data is speicifc and imperative
    # tokens = [tok for tok in tokens if tok not in STOPLIST]

    # stoplist symbols
    tokens = [tok for tok in tokens if tok not in SYMBOLS]

    # clean up whitespace and line breaks etc,.
    for tok in tokens:
        normalize_whitespace(tok)

    return tokens

def buildClassificationPipeline():
    
    # the vectorizer and classifer to use
    # note that I changed the tokenizer in CountVectorizer to use a custom function 'tokenizeText' using spaCy's tokenizer
    # CountVectorizer is ski_learn native class API to create feature vectosrs. In this case word frequency and bigrams.
    vectorizer = CountVectorizer(tokenizer=tokenizeText, ngram_range=(1,2))
    clf = svm.LinearSVC()
    #clf = naive_bayes.MultinomialNB()
    # the pipeline to clean, tokenize, vectorize, and classify
    yield Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer), ('clf', clf)])

def trainClassificationPipeline(pipeline=None, training_data=None):
    '''
     Args:
        pipeline: (scikit-learn Pipeline): Scikit-Learn Pipeline object
        training_data: (tuple<String[],String[]>): paired arrays of training documents and labels
    Returns:
        :class:``
    Raises:
        RuntimeError: if package can't be loaded
    '''
    if pipeline is None:
        pipeline = buildClassificationPipeline()
    if training_data is None:
        training_set = training_data[0]
        training_labels = training_data[1]
    else:
        training_set, training_labels = io('../resources/intents.json')
    yield pipeline.fit(training_set, training_labels)





