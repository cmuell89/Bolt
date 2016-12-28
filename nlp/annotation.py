"""
Created on Nov 2, 2016

@author: Carl Mueller
"""
from abc import abstractmethod, ABCMeta
from utils.exceptions import AnnotatorValidationError
import logging


class Annotation:
    """ Annotation object that is passed along a sequence of annotators """
    def __init__(self, original_text, key=None):
        """
        :param original_text: the original text passed into the annotation object, unadulterated
        :param key: the bot id used to obtain references in hashes to obtain bot specific models
        """
        self.annotations = dict()
        self.annotations['original_text'] = original_text
        self.annotations['key'] = key
        self.annotations['results'] = {"classification": [], "entities": []}
    
    
class AbstractAnnotator(metaclass=ABCMeta):
    """ Abstract class for Annotators """
    
    def __init__(self, name):
        self.name = name
        self.logger = logging.getLogger('BOLT.annotation')

    def validate_and_annotate(self, annotation):
        """
        Take the incoming annotation and return the updated annotation object by first validating that the current
        annotation object can be used by the Annotator and then runs the annotate method of the annotation.
        :param annotation: Annotation object to be updated.
        :return: If no exception raised, returns the altered annotation object. If an exception is raised in validate,
                 returns the orginal annotation passed into method call.
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


class IntentClassificationAnnotator(AbstractAnnotator):
    def __init__(self, name, classifier):
        self.classifier = classifier
        super().__init__(name)
    
    def validate(self, annotation):
        pass
        
    def annotate(self, annotation):
        """
        Runs the classifier.classify method on the original text and updates the Annotation object with the results.
        :param annotation: Annotation object to be updated
        :return: Updated annotation object
        """
        classification_results = self.classifier.classify(annotation.annotations['original_text'])
        annotation.annotations['stopwords'] = classification_results['stopwords']
        annotation.annotations['entity_types'] = classification_results['entity_types']
        annotation.annotations['results']['classification'] = classification_results['intents']
        return annotation


class BinaryClassificationAnnotator(AbstractAnnotator):
    def __init__(self, name, classifier):
        self.classifier = classifier
        super().__init__(name)

    def validate(self, annotation):
        pass

    def annotate(self, annotation):
        """
        Runs the classifier.classify method on the original text and updates the Annotation object with the results.
        :param annotation: Annotation object to be updated
        :return: Updated annotation object
        """
        result = self.classifier.classify(annotation.annotations['original_text'])
        annotation.annotations['results']['entities'].append({"name": self.name, "value": result})
        return annotation


class GazetteerAnnotator(AbstractAnnotator):
    def __init__(self, name, gazetteer, max_edit_distance=2):
        self.max_edit_distance = max_edit_distance
        self.gazetteer = gazetteer
        super().__init__(name)
        
    def validate(self, annotation):
        """
        Valiates that the annotation.annotations dict contains entity types with the name equal to the self.name of the
        current annotator.
        :param annotation: Annotation object to be updated
        :type annotation:
        :return: Updated annotation object
        """
        if not annotation.annotations['entity_types']:
            raise AnnotatorValidationError("No entity types found in annotation: " + self.name)
        # if self.name not in annotation.annotations['entity_types']:
        #     raise AnnotatorValidationError("Entity not found. No annotation performed for: " + self.name)

    def annotate(self, annotation):
        """
        Annotates the annotation object with the search results give the original text and the self.gazetteer gazetteer.
        Appends the gazetteer result to the annotation.annotations['results']['entities] list
        :param annotation: The annotation object to update
        :return: Returns the updated annotation object
        """
        stopwords = annotation.annotations['stopwords']
        text = annotation.annotations['original_text']
        result = self.gazetteer.search_query(text, stopwords, self.max_edit_distance)
        annotation.annotations['results']['entities'].append({"name": self.name, "value": result})
        return annotation


class RegexAnnotator(AbstractAnnotator):
    def __init__(self, name, regexer):
        self.regexer = regexer
        super().__init__(name)

    def validate(self, annotation):
        """
        Valiates that the annotation.annotations dict contains entity types with the name equal to the self.name of the
        current annotator.
        :param annotation: Annotation object to be updated
        :type annotation:
        :return: Updated annotation object
        """
        if not annotation.annotations['entity_types']:
            raise AnnotatorValidationError("No entity types found in annotation: " + self.name)
        # if self.name not in annotation.annotations['entity_types']:
        #     raise AnnotatorValidationError("Entity not found. No annotation performed for: " + self.name)

    def annotate(self, annotation):
        """
        Annotates the annotation object with the results of the Regexer object.
        Appends the results to the annotation.annotations['results']['entities] list
        :param annotation: The annotation object to update
        :return: Returns the updated annotation object
        """
        matches = self.regexer.get_matches(annotation.annotations['original_text'])
        annotation.annotations['results']['entities'].append({"name": self.name, "value": matches})
        return annotation
