"""
Created on Nov 3, 2016

@author: Carl Mueller
@company: Lightning in a Bot, Inc
"""
import os
import logging
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor
from nlp.annotation import IntentClassificationAnnotator, BinaryClassificationAnnotator,\
                           GazetteerAnnotator, RegexAnnotator, Annotation
from nlp.ner.gazetteer import GazetteerModelAccessor, GazetteerModelBuilder
from nlp.ner.regexer import Regexer

logger = logging.getLogger('BOLT.nlp')

clf_builder = ClassificationModelBuilder()
gaz_builder = GazetteerModelBuilder()

clf_builder.update_serialized_model('svm', multiclass='true', binary='true')
environment = os.environ.get('ENVIRONMENT')
if environment == 'prod' or environment == 'dev':
    gaz_builder.initialize_gazetteer_models()

# TODO: Convert all entities to useing underscore. This will affect gazetteer files.

class Updater:
    """
    Updater objects are used to update classification and gazetteer models based on type and key.
    """
    def __init__(self):
        self.gaz_builder = GazetteerModelBuilder()
        self.clf_builder = ClassificationModelBuilder()
    
    def update_classifier(self, skl_classifier, **kwargs):
        """
        Updates the classifier passed in as a parameter
        :param skl_classifier: type of classifier to be trained/updated; 'svm' or 'nb'
        """
        self.clf_builder.update_serialized_model(skl_classifier, **kwargs)
        
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

    def run_analysis(self, query, key=None):
        # TODO CREATE CLF_PIPELINE AND THEN ENTITY_PIPELINE
        """
        Builds an AnalysisPipeline objects and the set of Annotator objects to be used in the pipeline.
        Runs the analysis and retruns the 'results' value of the Annotation object's annotations dict.
        :param query: The query text to be analyzed
        :param key: unique identification key for the gazetteer type; usually bot key
        :return: dict of results
        """
        logger.info("Running analysis on query...")
        core_annotation = Annotation(query, key)
        clf_pipeline = AnalysisPipeline()
        entity_pipeline = AnalysisPipeline()
        clf = self.clf_accessor.get_classification_pipeline('multiclass', 'intent_classifier')

        """ Create the intent classifier Annotator 'clf' """
        clf_annotator = IntentClassificationAnnotator('clf', clf)
        clf_pipeline.add_annotator(clf_annotator)
        """ Run clf_pipeline to obtain intent classification """
        core_annotation = clf_pipeline.analyze(core_annotation)
        """ Create annotators based on entity types of intent classification """
        entities = core_annotation.annotations['entity_types']

        """ Access the binary classifier for the appropriate entity types and create BinaryClassifierAnnotator"""
        for entity in entities:
            if entity['entity_type'] == 'binary':
                logger.debug("Creating BinaryClassificationAnnotator for: ")
                logger.debug(entity['entity_name'])
                clf = self.clf_accessor.get_classification_pipeline('binary', entity['entity_name'])
                binary_clf_annotator = BinaryClassificationAnnotator(entity['entity_name'], clf)
                entity_pipeline.add_annotator(binary_clf_annotator)

        """ Access the gazetteer for the appropriate entity types and create an GazetteerAnnotator """
        gazetteers = self.gaz_accessor.get_gazeteers(key)
        if gazetteers is not None:
            for entity in entities:
                if entity['entity_type'] == 'gazetteer' or entity['entity_type'] == 'simple-gazetteer':
                    logger.debug("Creating GazetterAnnotator for: ", entity)
                    gaz_annotator = GazetteerAnnotator(entity['entity_name'], gazetteers[entity['entity_name']])
                    entity_pipeline.add_annotator(gaz_annotator)

        """ Create a RegexAnnotator for each regex entity type"""
        for entity in entities:
            if entity['entity_type'] == 'regex':
                logger.debug("Creating RegexAnnotator for: ", entity)
                regex_annotator = RegexAnnotator(entity['entity_name'], Regexer(entity['regular_expressions']))
                entity_pipeline.add_annotator(regex_annotator)

        core_annotation = entity_pipeline.analyze(core_annotation)
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