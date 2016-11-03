from .clf.classification import build_classification_pipeline, train_classification_pipeline
from .annotation import ClassificationAnnotator, GazetteerAnnotator
from .ner import gazetteer

__CLF__ = build_classification_pipeline()

__GAZETTEERS__ = {}


class Analyzer:
    
    def run_analysis(self):
        clf_annotator = ClassificationAnnotator('clf', __CLF__)
        gazetteer = GazetteerAnnotator()
        pipeline = AnalysisPipeline(clf_annotator)
    
    def update_classifier(self, classifier_type='svm'):
        global __CLF__
        __CLF__ = train_classification_pipeline(None, None, classifier_type)
    
    

class AnalysisPipeline:
    def __init__(self, annotator_sequence):
        self.sequence = annotator_sequence
    
    def analyze(self, annotation):
        for annotator in self.sequence:
            annotation = annotator.validate_and_annotate(annotation)
        return annotation
    
    def __str__(self):
        return [(annotator.name, annotator) for annotator in self.sequence]
    
