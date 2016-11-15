"""
Created on Nov 3, 2016

@author: Carl Mueller
@company: Lightning in a Bot, Inc

"""
from nlp.clf.classification import ClassificationModelBuilder, ClassificationModelAccessor
from nlp.annotation import ClassificationAnnotator, GazetteerAnnotator, Annotation
from nlp.ner.gazetteer import GazetteerModelAccessor, GazetteerModelBuilder

""" For test only """
import settings
import timeit
from pprint import PrettyPrinter


clf_builder = ClassificationModelBuilder()
gaz_builder = GazetteerModelBuilder()

clf_builder.update_serialized_model()
gaz_builder.create_new_gazetteer_model("product_name", 1234)


class Updater:
    def __init__(self):
        self.gaz_builder = GazetteerModelBuilder()
        self.clf_builder = ClassificationModelBuilder()
    
    def update_classifier(self, skl_classifier): 
        self.clf_builder.update_serialized_model(skl_classifier)
        
    def update_gazetteer(self, gazetteer_type=None, id_=None):
        self.gaz_builder.update_single_gazetteer_model(gazetteer_type, id_)


class Analyzer:
    def __init__(self):
        self.gaz_accessor = GazetteerModelAccessor()
        self.clf_accessor = ClassificationModelAccessor()

    def run_analysis(self, query, id_):
        core_annotation = Annotation(query, id_)
        pipeline = AnalysisPipeline()
        gazetteers = self.gaz_accessor.get_gazeteers(id_)
        clf = self.clf_accessor.get_classification_pipeline('intent_classifier')
        clf_annotator = ClassificationAnnotator('clf', clf)
        pipeline.add_annotator(clf_annotator)
        for gazetteer in gazetteers:
            gaz_annotator = GazetteerAnnotator(gazetteer, gazetteers[gazetteer])
            pipeline.add_annotator(gaz_annotator)
        core_annotation = pipeline.analyze(core_annotation)
        return core_annotation.annotations['results']


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
    

query = ''
while query != "exit":
    query = input("Enter query:\n")
    start = timeit.default_timer()
    analyzer = Analyzer()
    result = analyzer.run_analysis(query, 1234)
    pp = PrettyPrinter(indent=4)
    pp.pprint(result)
    print("\nExecution time to obtain NLP results:")
    print((timeit.default_timer() - start)/100000)
    print()