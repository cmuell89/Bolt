"""
Created on Nov 3, 2016

@author: Carl Mueller
@company: Lightning in a Bot, Inc
"""
import os
import logging
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor
from nlp.annotation import ClassificationAnnotator, GazetteerAnnotator, RegexAnnotator, Annotation
from nlp.ner.gazetteer import GazetteerModelAccessor, GazetteerModelBuilder
from nlp.ner.regexer import Regexer

logger = logging.getLogger('BOLT.nlp')

clf_builder = ClassificationModelBuilder()
gaz_builder = GazetteerModelBuilder()

clf_builder.update_serialized_model()
environment = os.environ.get('ENVIRONMENT')
if environment == 'prod':
    gaz_builder.initialize_gazetteer_models()


class Updater:
    """
    Updater objects are used to update classification and gazetteer models based on type and key.
    """
    def __init__(self):
        self.gaz_builder = GazetteerModelBuilder()
        self.clf_builder = ClassificationModelBuilder()
    
    def update_classifier(self, skl_classifier):
        """
        Updates the classifier passed in as a parameter
        :param skl_classifier: type of classifier to be trained/updated; 'svm' or 'nb'
        """
        self.clf_builder.update_serialized_model(skl_classifier)
        
    def update_gazetteer(self, gazetteer_type=None, key=None):
        """
        Updates a gazetteer model for the given gazetteer_type and key idenfier
        :param gazetteer_type: type of gazetteer
        :param key: unique identification key for the gazetteer type; usually bot key
        """
        self.gaz_builder.update_single_gazetteer_model(gazetteer_type, key)


class Analyzer:
    """
    Analyzer objects used to run NLP analysis on queries using AnalysisPipelines and Annotators
    """
    def __init__(self):
        self.gaz_accessor = GazetteerModelAccessor()
        self.clf_accessor = ClassificationModelAccessor()

    def run_analysis(self, query, key):
        """
        Builds an AnalysisPipeline objects and the set of Annotator objects to be used in the pipeline.
        Runs the analysis and retruns the 'results' value of the Annotation object's annotations dict.
        :param query: The query text to be analyzed
        :param key: unique identification key for the gazetteer type; usually bot key
        :return: dict of results
        """
        logger.info("Running analysis on query...")
        core_annotation = Annotation(query, key)
        pipeline = AnalysisPipeline()
        gazetteers = self.gaz_accessor.get_gazeteers(key)
        clf = self.clf_accessor.get_classification_pipeline('intent_classifier')

        """ Create the intent classifier Annotator 'clf' """
        clf_annotator = ClassificationAnnotator('clf', clf)
        pipeline.add_annotator(clf_annotator)

        """ for each type of gazetteer create an GazetteerAnnotator """
        if gazetteers is not None:
            for gazetteer in gazetteers:
                gaz_annotator = GazetteerAnnotator(gazetteer, gazetteers[gazetteer])
                pipeline.add_annotator(gaz_annotator)

        """ order name RegexAnnotator """
        order_name_regexer = RegexAnnotator('order_name', Regexer([r'([A-Za-z]*|#)[0-9]+']))
        pipeline.add_annotator(order_name_regexer)

        """ out-of-state RegexAnnotator """
        out_of_state_regexer = RegexAnnotator('out_of_state', Regexer([r'(out of state)',
                                                                       r'(out-of-state)',
                                                                       r'(((outside|out side)) of)',
                                                                       r'(outside|out side)']))
        pipeline.add_annotator(out_of_state_regexer)

        core_annotation = pipeline.analyze(core_annotation)
        return core_annotation.annotations['results']


class AnalysisPipeline:
    """
    AnalysisPipeline objects store a sequence of annotators that iteratively analyzes a query.
    """
    def __init__(self, *args):
        self.sequence = list()
        if args is not None:
            for arg in args:
                self.sequence.append(arg)
      
    def add_annotator(self, annotator):
        """
        Adds annotators to the sequence of the class instance
        :param annotator: Annotator to be added to the sequence of the pipeline
        """
        self.sequence.append(annotator)
          
    def analyze(self, annotation):
        """
        Iterates over Annotators in the the self.seqeuence, reassigning the annotation
        to the current annotation results
        :param annotation: Annotation object to collect and store annotator reulst
        :return: Returns the annotation object
        """
        for annotator in self.sequence:
            annotation = annotator.validate_and_annotate(annotation)
        return annotation
      
    def __str__(self):
        return [(annotator.name, annotator) for annotator in self.sequence]