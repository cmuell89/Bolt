'''
Created on Nov 3, 2016

@author: Carl Mueller
@company: Lightning in a Bot, Inc
'''
from nlp.clf.classification import build_classification_pipeline, train_classification_pipeline
from nlp.annotation import ClassificationAnnotator, GazetteerAnnotator, Annotation
from nlp.ner.gazetteer import GazetteerModelAccessor, GazetteerModelBuilder

""" For test only """
import settings
from pprint import PrettyPrinter

pipeline = build_classification_pipeline('svm')
clf = train_classification_pipeline(pipeline)
builder = GazetteerModelBuilder()
builder.create_new_gazetteer_model("product_names", 1234)


class Analyzer:
    def __init__(self):
        self.gaz_accessor = GazetteerModelAccessor()

    
    def run_analysis(self, query, bot_id):
        annotation = Annotation(query, bot_id)
        pipeline = AnalysisPipeline()
        gazetteers = self.gaz_accessor.get_gazzeteers(["product_names"], 1234)
        
        global clf
        clf_annotator = ClassificationAnnotator('clf', clf)
        pipeline.add_annotator(clf_annotator)
        for gazetteer in gazetteers:
            gaz_annotator = GazetteerAnnotator(gazetteer, gazetteers[gazetteer])
            pipeline.add_annotator(gaz_annotator)
             
        annotation = pipeline.analyze(annotation)
        return annotation.annotations['results']
         
class AnalysisPipeline:
    def __init__(self, *args):
        self.sequence = list()
        if args is not None:
            for arg in args:
                self.sequence.append(arg)
      
    def add_annotator(self, annotator):
        self.sequence.append(annotator)
          
    def analyze(self, annotation):
        for annotator in self.sequence:
            annotation = annotator.validate_and_annotate(annotation)
        return annotation
      
    def __str__(self):
        return [(annotator.name, annotator) for annotator in self.sequence]
    
analyzer = Analyzer()
query = ''
while(query != "exit"):
    query = input("Enter query:\n")
    result = analyzer.run_analysis(query, 1234)
    pp = PrettyPrinter(indent=4)
    pp.pprint(result)
    print()