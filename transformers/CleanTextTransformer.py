'''
Created on Jul 4, 2016

@author: carl
'''

from sklearn.base import TransformerMixin

from models.spacy_model import load_spacy_pipeline


# load Spacy parser    
parser = load_spacy_pipeline

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


# A custom function to clean the text before sending it into the vectorizer
def cleanText(text):
    # get rid of newlines
    text = text.strip().replace("\n", " ").replace("\r", " ")
    
    # lowercase, perhaps not a good thing for proper nouns?
    text = text.lower()
    
    return text