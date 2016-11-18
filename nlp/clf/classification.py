"""
Created on May 28, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc

Functions managing the prototype classifier.
"""

import string
import logging
import pickle
from sklearn import svm, naive_bayes
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from models.spacy_model import load_spacy
from transformers.clean_text_transformer import CleanTextTransformer
from database.database import IntentsDatabaseEngine
from utils import io
from utils.string_cleaners import normalize_whitespace

# load Spacy pipeline from cached model    
spacy_nlp = load_spacy('en')
logger = logging.getLogger('BOLT.clf')

# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]

# Dict referencing pickled classifiers.
CLASSIFIERS = {}


class ClassificationModelBuilder:
    """
    Builds classification models stored in the global dict CLASSIFIERS
    """
    def update_serialized_model(self, skl_classifier=None):
        """
        Saves to the global dict CLASSIFIERS a pickled (serialized) fitted Scikit-learn model
        :param skl_classifier: type of classifier (svm, nb)
        """
        global CLASSIFIERS
        fitted_pipeline = self._train_classification_pipeline(None, None, skl_classifier)
        CLASSIFIERS['intent_classifier'] = pickle.dumps(fitted_pipeline)
    
    def _train_classification_pipeline(self, pipeline=None, training_data=None, skl_classifier=None):
        """
        Trains the Scikit-Learn Pipeline object via the fit methods and the provided or default training data
        :param pipeline: Scikit-Learn Pipeline object
        :param training_data: paired arrays of training documents and labels
        :param skl_classifier: string that indicates the type of classification algorithm to use (svm, nb)
        :return: fitted sci-kit learn pipeline object
        """
        if skl_classifier is None:
            skl_classifier = 'svm'
        if pipeline is None:
            pipeline = self._build_classification_pipeline(skl_classifier)
        if training_data is None:
            training_set, training_labels = io.create_data_for_pipeline_from_database()
            logger.debug("Using data from DB for training")
        else:
            training_set = training_data[0]
            training_labels = training_data[1]
        logger.debug("Fitting sklearn pipeline to data")
        return pipeline.fit(training_set, training_labels)
    
    def _build_classification_pipeline(self, skl_classifier=None):
        """
        Function that builds a sklearn pipeline.
        Currently the estimators used in this build function are hard-coded
        Estimators/Transformers:
            CleanTextTransformer: Custom class to clean text
            CountVectorizor: sklearn native transfomer
                Note that I changed the tokenizer in CountVectorizer to use a custom function 'tokenizeText' using spaCy's tokenizer
            LinearSVC(): Multitlcass capable support vector machine
            MultinomialNB(): Multinomial Naive Bayes classifier
        :param skl_classifier: classifier type (svm, nb)
        :return: Scikit-learn Pipeline object, unfitted
        """
        if skl_classifier is None:
            skl_classifier = 'svm'
        vectorizer = CountVectorizer(tokenizer=self._tokenize_text, ngram_range=(1, 2))
        if skl_classifier == 'svm':
            logger.debug("Creating LinearSVC classifier")
            clf = svm.LinearSVC()
        elif skl_classifier == 'nb':
            logger.debug("Creating Multinomial Naive Bayes classifier")
            clf = naive_bayes.MultinomialNB()
        calibrated_clf = CalibratedClassifierCV(clf)
        return Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', vectorizer), ('clf', calibrated_clf)])
    
    def _tokenize_text(self, sample):
        """
        Function that tokenizes, lemmatizes, removes potential stopwords/stop-symbols, and cleans whitespace.
        Lemmas may be useful only for intent classification but not other types of functionality (traits like plurality etc,.)
        :param sample: sample of text to be tokenized
        :return: returns the tokens of the sample
        """
        sample = normalize_whitespace(sample)
        tokens = spacy_nlp(sample)
            
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


class ClassificationModelAccessor:
    """
    Class providing methods to access classification models
    """
    def get_classification_pipeline(self, classifier_type):
        """
        Loads the pickled classifier from the global CLASSIFIERS dict and returns a Classifier object
        :param classifier_type:
        :return: the Classifier object build from the pickled object from the CLASSIFIERS global dict
        """
        global CLASSIFIERS
        pipeline = pickle.loads(CLASSIFIERS[classifier_type])
        classifier = Classifier(pipeline)
        return classifier


class Classifier:
    """
    Class instances returned from ClassificationBuilder to be used the the analysis and update modules to manage NLP
    """
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.db = IntentsDatabaseEngine()

    def __exit__(self):
        self.db.release_database_connection()

    def classify(self, document):
        """
        Classifies the document and provides additional data based on those classification results
        :param document:
        :type document:
        :return: Returns of a dict that contains the top3 classification results (which includes their confidences),
                 the entity types and stopwords associated with the top (highest confidence) classification result
        """
        results = {}
        top_3 = []
        classes = self.pipeline.classes_.tolist()
        class_probabilities = self.pipeline.predict_proba([document]).tolist()
        confidence_metrics = list(zip(classes, class_probabilities[0]))
        intents = sorted(confidence_metrics, key=lambda tup: tup[1], reverse=True)
        for i in range(3):
            tup = intents[i]
            top_3.append({"intent": tup[0], "confidence": tup[1]})
        # The dababase call returns a single tuple for which the list of entities and stopwords is the second element.
        intent_entities = self.db.get_intent_entities(intents[0][0])[0][1]
        intent_stopwords = self.db.get_intent_stopwords(intents[0][0])[0][1]
        results['intents'] = top_3
        results['entity_types'] = intent_entities
        results['stopwords'] = intent_stopwords
        return results
    




