'''
Created on Nov 2, 2016

@author: Carl Mueller
'''
from abc import abstractmethod
from nlp import TagSearcher

class Annotation:
    """ Annotation object that is passed along a sequence of annotators """
    def __init__(self, original_text, bot_id):
        """
        Parameters
        ----------
        
        original_text: the original text passed into the annotation object, unadulterated
        bot_id: the bot id used to obtain references in hashes to obtain bot specific models
        """
        self.annotations = {}
        self.annotations['original_text'] = original_text
        self.annotations['id'] = bot_id
        self.annotations['results'] = {}
    
    
class AbstractAnnotator:
    """ Mixin class for annotators used in nlp pipeline """
    
    def __init__(self, name):
        self.name = name
    
    def validate_and_annotate(self, annotation):
        """ 
        Take the incoming annotation and return the updated annotation object
        
        This method is called by the a pipeline object
        
        This method first validates that the current annotation object can be used by 
        the extending Annotator
        
        which uses the in turn calls
        the annotate method of the class extending this mixin.
        
        Parameters
   ...
        ----------
        
        annotation: the annotation object that is passed along to each annotator
                    in the sequence
        """
        try:
            self.validate(annotation)
            return self.annotate(annotation)
        except annotation.ValidationError as e:
            return annotation['results'][self.name] = "Failure"
    
    @abstractmethod
    def validate(self):
        pass
    
    @abstractmethod
    def annotate(self):
        pass
    
class ClassificationAnnotator(AbstractAnnotator):
    def __init__(self, name, classifier):
        self.classifier = classifier
        super().__init__(name)
    
    def validate(self):
        pass
        
    def annotate(self, annotation):
        classification_results = self.classifier.classify(annotation['original_text'])
        annotation['stopwords'] = classification_results['stopwords']
        annotation['results']['classification'] = classification_results['results']
        return annotation

class GazetteerAnnotator(AbstractAnnotator):
    def __init__(self, name, max_cost=2, gazetteer_dict):
        self.searcher = TagSearcher()
        self.max_cost = max_cost
        self.gazetteer_dict = gazetteer_dict
        super().__init__(name)
        
    def validate(self):
        pass  
    
    def annotate(self, annotation):
        gazetteer_trie = self.gazetteer_dict(annotation['bot_id'])
        stopwords = self.get_custom_stopwords(annotation['stopwords'])
        text = annotation['original_text']
        results = self.searcher.get_tag(gazetteer_trie, text, stopwords, self.max_cost)
        return results