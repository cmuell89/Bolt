"""
Created on Nov 2, 2016

@author: Carl Mueller
"""
from abc import abstractmethod, ABCMeta
from utils.exceptions import AnnotatorValidationError
import logging


class Annotation:
    """ Annotation object that is passed along a sequence of annotators """
    def __init__(self, original_text, id_):
        """
        Parameters
        ----------
        
        original_text: the original text passed into the annotation object, unadulterated
        bot_id: the bot id used to obtain references in hashes to obtain bot specific models
        """
        self.annotations = {}
        self.annotations['original_text'] = original_text
        self.annotations['id'] = id_
        self.annotations['results'] = {}
    
    
class AbstractAnnotator(metaclass=ABCMeta):
    """ Mixin class for annotators used in nlp pipeline """
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('BOLT.annotation')

    def validate_and_annotate(self, annotation):
        """ 
        Take the incoming annotation and return the updated annotation object
        
        This method is called by the a pipeline object
        
        This method first validates that the current annotation object can be used by 
        the extending Annotator
        
        which uses the in turn calls
        the annotate method of the class extending this mixin.
        
        Parameters
        ----------
        
        annotation: the annotation object that is passed along to each annotator
                    in the sequence
        """
        try:
            self.validate(annotation)
            return self.annotate(annotation)
        except AnnotatorValidationError as e:
            self.logger.debug(e.value)
            return annotation
    
    @abstractmethod
    def validate(self):
        """ Raises a Validation Error if requirements are not meant """
        pass
    
    @abstractmethod
    def annotate(self):
        pass


class ClassificationAnnotator(AbstractAnnotator):
    def __init__(self, name, classifier):
        self.classifier = classifier
        super().__init__(name)
    
    def validate(self, annotation):
        pass
        
    def annotate(self, annotation):
        classification_results = self.classifier.classify(annotation.annotations['original_text'])
        annotation.annotations['stopwords'] = classification_results['stopwords']
        annotation.annotations['entity_types'] = classification_results['entity_types']
        annotation.annotations['results']['classification'] = classification_results['results']
        return annotation


class GazetteerAnnotator(AbstractAnnotator):
    def __init__(self, name, gazetteer, max_edit_distance=2):
        self.max_edit_distance = max_edit_distance
        self.gazetteer = gazetteer
        super().__init__(name)
        
    def validate(self, annotation):
        if not annotation.annotations['entity_types']:
            raise AnnotatorValidationError("No entity types found in annotation")
        if self.name not in annotation.annotations['entity_types']:
            raise AnnotatorValidationError("Annotator validation error for: " + self.name)

    def annotate(self, annotation):
        stopwords = annotation.annotations['stopwords']
        text = annotation.annotations['original_text']
        result = self.gazetteer.search_query(text, stopwords, self.max_edit_distance)
        annotation.annotations['results'][self.name] = result
        return annotation
