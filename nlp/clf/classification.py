"""
Created on May 28, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc

Functions managing the prototype classifier.
"""

import string
import logging
import pickle
from functools import partial
from abc import abstractmethod, ABCMeta
from sklearn import svm, naive_bayes
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.calibration import CalibratedClassifierCV
from models.spacy_model import load_spacy
from transformers.clean_text_transformer import CleanTextTransformer
from database.database import IntentsDatabaseEngine, EntitiesDatabaseEngine
from utils import io
from utils.string_cleaners import normalize_whitespace

# load Spacy pipeline from cached model    
spacy_nlp = load_spacy('en')
logger = logging.getLogger('BOLT.clf')

# List of symbols we don't care about
SYMBOLS = " ".join(string.punctuation).split(" ") + ["-----", "---", "...", "“", "”", "'ve"]

# Dict referencing pickled classifiers.
CLASSIFIERS = {'multiclass': {}, 'binary_classifier': {}}


class ClassificationModelBuilder:
    """
    Builds classification models stored in the global dict CLASSIFIERS
    """
    def initialize_classification_models(self, multiclass=False, binary_classifier=False):
        """
        Saves to the global dict CLASSIFIERS a pickled (serialized) fitted Scikit-learn model
        :param skl_classifier: type of classifier used for intent classification (svm, nb)
        :param multiclass: true/false on whether to update multiclass classifiers stored in CLASSIFIERS
        :param multiclass: true/false on whether to update binary classifiers stored in CLASSIFIERS
        """
        db = EntitiesDatabaseEngine()
        results = db.get_entities()
        binary_classifier_entities = []
        for result in results:
            if result[2] == 'binary_classifier':
                binary_classifier_entities.append(result)

        logger.debug("Updating serialized classifier.")
        global CLASSIFIERS
        """ Update globally stored classifier models"""

        if multiclass:
            """ Build, train, and save intent classification pipeline """
            logger.debug("INITIALIZING: all multiclass classifiers.")
            # TODO Work on default classifier algorithm choice. Perhaps remove choice entirely.
            fitted_intent_classification_pipeline = self._train_intent_classification_pipeline(None, None, None)
            CLASSIFIERS['multiclass']['intent_classifier'] = pickle.dumps(fitted_intent_classification_pipeline)

        if binary_classifier:
            """ Build, train, and save binary classification pipelines """
            logger.debug("INITIALIZING: all binary classifiers.")
            for binary_entity in binary_classifier_entities:
                logger.debug("Building binary classifier for: {0}".format(binary_entity[1]))
                pipeline = self._build_binary_classification_pipeline(binary_entity[6])
                fitted_binary_classification_pipeline = self._train_binary_classfication_pipeline(pipeline, binary_entity[3], binary_entity[4])
                CLASSIFIERS['binary_classifier'][binary_entity[1]] = pickle.dumps(fitted_binary_classification_pipeline)

    def update_classification_model(self, classifier_type, classifier_name):
        if classifier_type == 'multiclass':
            fitted_intent_classification_pipeline = self._train_intent_classification_pipeline(None, None, None)
            CLASSIFIERS['multiclass']['intent_classifier'] = pickle.dumps(fitted_intent_classification_pipeline)

        if classifier_type == 'binary_classifier':
            db = EntitiesDatabaseEngine()
            entity_info = db.get_entity(classifier_name)[0]
            pipeline = self._build_binary_classification_pipeline(entity_info[6])
            fitted_binary_classification_pipeline = self._train_binary_classfication_pipeline(pipeline,
                                                                                              entity_info[3],
                                                                                              entity_info[4])
            CLASSIFIERS['binary_classifier'][entity_info[1]] = pickle.dumps(
                        fitted_binary_classification_pipeline)


    def _train_intent_classification_pipeline(self, pipeline=None, training_data=None, skl_classifier=None):
        """
        Trains the Scikit-Learn Pipeline object via the fit methods and the provided or default training data
        :param pipeline: Scikit-Learn Pipeline object
        :param training_data: paired arrays of training documents and labels
        :param skl_classifier: string that indicates the type of classification algorithm to use (svm, nb)
        :return: fitted sci-kit learn pipeline object
        """
        logger.debug("Training classification pipeline.")
        if skl_classifier is None:
            skl_classifier = 'svm'
        if pipeline is None:
            pipeline = self._build_intent_classification_pipeline(skl_classifier)
        if training_data is None:
            training_set, training_labels = io.create_data_for_intent_pipeline_from_database()
            logger.debug("Using data from DB for training")
        else:
            training_set = training_data[0]
            training_labels = training_data[1]
        logger.debug("Fitting sklearn pipeline to data")
        return pipeline.fit(training_set, training_labels)

    def _train_binary_classfication_pipeline(self, pipeline, positive_expressions, negative_expressions):
        logger.debug("Training binary classifier")
        training_set = []
        training_labels = []
        if len(positive_expressions) > 0 and len(negative_expressions) > 0:
            for exp in positive_expressions:
                training_set.append(exp)
                training_labels.append('true')
            for exp in negative_expressions:
                training_set.append(exp)
                training_labels.append('false')
            return pipeline.fit(training_set, training_labels)
        else:
            raise Exception()
    
    def _build_intent_classification_pipeline(self, skl_classifier=None):
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

    def _build_binary_classification_pipeline(self, keywords):
        """
        Function build the an sklearn pipeline for binary classification.
        :param keywords:
        :return:
        """
        """ Sci-kit learn vectorizors are combined toegether using FeatureUnion """
        vocabulary_vectorizer = CountVectorizer(vocabulary=keywords)
        ngram_vectorizer = CountVectorizer(analyzer='char_wb', ngram_range=(2, 5), min_df=1)
        tokenize_text = partial(self._tokenize_text, lemmatize=True)
        vectorizer = CountVectorizer(tokenizer=tokenize_text, ngram_range=(1, 2))
        combined_vectorizer = FeatureUnion([("ngram", ngram_vectorizer),
                                            ("token", vectorizer),
                                            ("vocab", vocabulary_vectorizer)])

        """ Feature Selectioin performed using term frequency inverse document frequency (TFIDF) procedure """
        tfidf = TfidfTransformer(norm='l2', use_idf=True)

        """ Linear SCV classifier type calibrated to obtain confidence results """
        linearSVC_clf = svm.LinearSVC()
        calibrated_clf = CalibratedClassifierCV(linearSVC_clf)
        return Pipeline([('cleanText', CleanTextTransformer()), ('vectorizer', combined_vectorizer), ('tfidf', tfidf),
                         ('clf', calibrated_clf)])

    def _tokenize_text(self, sample, lemmatize=True):
        """
        Function that tokenizes, lemmatizes, removes potential stopwords/stop-symbols, and cleans whitespace.
        Lemmas may be useful only for intent classification but not other types of functionality (traits like plurality etc,.)
        :param sample: sample of text to be tokenized
        :return: returns the tokens of the sample
        """
        sample = normalize_whitespace(sample)
        tokens = spacy_nlp(sample)
            
        # lemmatize
        if lemmatize:
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
    def get_classification_pipeline(self, classifier_type, classifier_name):
        """
        Loads the pickled classifier from the global CLASSIFIERS dict and returns a Classifier object
        :param classifier_type: multiclass/binary the type of classifer to access from CLASSIFIERS
        :param classifier_name: name of classifier to access from CLASSIFIERS
        :return: the Classifier object build from the pickled object from the CLASSIFIERS global dict
        """
        global CLASSIFIERS
        if classifier_type in CLASSIFIERS.keys() and classifier_name in CLASSIFIERS[classifier_type].keys():
            pipeline = pickle.loads(CLASSIFIERS[classifier_type][classifier_name])
            if classifier_name == 'intent_classifier':
                return IntentClassifier(pipeline)
            if classifier_type == 'binary_classifier':
                return BinaryClassifier(pipeline)
        else:
            return None


class AbstractClassifier(metaclass=ABCMeta):
    def __init__(self, pipeline):
        self.pipeline = pipeline

    @abstractmethod
    def classify(self, document):
        pass


class BinaryClassifier(AbstractClassifier):
    """
    Class that implements AbstractClassifier and builds a object that provides binary classification results
    """
    def __init__(self, pipeline):
        self.db = IntentsDatabaseEngine()
        super().__init__(pipeline)

    def classify(self, document):
        """
        Classifies the document with a binary classification results including the strength of the confidence.
        :param document: document to be classified
        :return: returns a list of classification results including confidence metrics
        """
        classes = self.pipeline.classes_.tolist()
        class_probabilities = self.pipeline.predict_proba([document]).tolist()
        confidence_metrics = list(zip(classes, class_probabilities[0]))
        classification_results = sorted(confidence_metrics, key=lambda tup: tup[1], reverse=True)
        return classification_results


class IntentClassifier(AbstractClassifier):
    """
    Class that implements  returned from ClassificationBuilder to be used the the analysis and update modules to manage NLP
    """
    def __init__(self, pipeline):
        self.db = IntentsDatabaseEngine()
        super().__init__(pipeline)

    def classify(self, document):
        """
        Classifies the document and provides additional data based on those classification results
        :param document: document to be classified
        :return: Returns of a dict that contains the top3 classification results (which includes their confidences),
                 the entity types and stopwords associated with the top (highest confidence) classification result
        """
        results = {}
        top_3 = []
        classes = self.pipeline.classes_.tolist()
        class_probabilities = self.pipeline.predict_proba([document]).tolist()
        confidence_metrics = list(zip(classes, class_probabilities[0]))
        intents_results = sorted(confidence_metrics, key=lambda tup: tup[1], reverse=True)
        for i in range(3):
            tup = intents_results[i]
            top_3.append({"intent": tup[0], "confidence": tup[1]})
        top_intent_name = intents_results[0][0]
        stopwords_db_results = self.db.get_intent_stopwords(top_intent_name)
        intent_stopwords = stopwords_db_results[0][1]
        intent_entities = self.db.get_intent_entities(top_intent_name)
        self.db.release_database_connection()
        entities = []
        for result in intent_entities:
            entity = {
                "entity_name": result[0],
                "entity_type": result[1],
                "regular_expressions": result[4]
            }
            entities.append(entity)
        results['intents'] = top_3
        results['entity_types'] = entities
        results['stopwords'] = intent_stopwords
        return results
    




