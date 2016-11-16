"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
import json
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from utils.string_cleaners import remove_apostrophe, normalize_whitespace, remove_question_mark, dash_to_single_space
from database.database import ExternalDatabaseEngine
from nlp.ner.trie import TrieBuilder, DictionaryBuilder, TrieNode

GAZETTEERS = {}


class GazetteerModelBuilder:
    
    def initialize_gazetteer_models(self):
        """
        Builds from scratch the entire GAZETTEERS dict

        Exceptions:
        -----------
        """
        global GAZETTEERS
        gazetteer_types = ['product_name', 'product_type', 'vendor']
        db = ExternalDatabaseEngine()
        keys = db.get_keys()
        for key in keys:
            for gaz_type in gazetteer_types:
                self.create_new_gazetteer_model(gaz_type, key)
        print(GAZETTEERS)
 
    def create_new_gazetteer_model(self, gazetteer_type, id_):
        """
        Creates a single gazetteer in the global dictionary GAZETTEERS
        
        Parameters:
        -----------
            gazetteer_type: the type of gazetteer. Example: product_name, product_type, vendor etc,.
            _id: the id used to access the specific gazetteer hashed within the dictionary.
            
        Exceptions:
        -----------
            TODO
        
        """
        global GAZETTEERS
        trie_builder = TrieBuilder()
        entities = self._get_entities_from_external_database(gazetteer_type, id_)
        entities = [x for x in entities if x is not None]
        if len(entities) > 0:
            new_trie = trie_builder.build_trie_from_dictionary(entities)
            new_gazetteer = Gazetteer(new_trie)
            if gazetteer_type not in GAZETTEERS:
                GAZETTEERS[gazetteer_type] = {}
                GAZETTEERS[gazetteer_type][id_] = new_gazetteer
            else:
                GAZETTEERS[gazetteer_type][id_] = new_gazetteer
    
    def update_single_gazetteer_model(self, gazetteer_type, id_):
        """
        Updates a single gazetteer in the global dictionary GAZETTEERS
        
        Parameters:
        -----------
        
        gazetteer_type: the type of gazetteer. Example: product_name, product_type, vendor etc,.
        _id: the id used to access the specific gazetteer hashed within the dictionary.
        
        Exceptions:
        -----------
            TODO
            
        """
        global GAZETTEERS
        trie_builder = TrieBuilder()
        
        if gazetteer_type in GAZETTEERS:
            entities = self._get_entities_from_external_database(gazetteer_type, id_)
            new_trie = trie_builder.build_trie_from_dictionary(entities)
            new_gazetteer = Gazetteer(new_trie)
            GAZETTEERS[gazetteer_type][id_] = new_gazetteer

    def _get_entities_from_external_database(self, gazetteer_type, id_):
        """
        Obtain the entities that will be used used to train a gazetteer model
        
        Parameters
        ----------
        id_: The id that will differentiate entity lists in the database
        gazetteer_type: The type of entity list to be retrieved from the database
        
        Exceptions
        ----------
        TODO

        """

        def entities_function_generator(entity_type):
            """
            Contains a dict. key: entity type; value: function that returns entities by id_
            :param entity_type:
            :return: function returning entities for given id_ for the entity type
            """
            db = ExternalDatabaseEngine()
            drivers = {'product_name': db.get_product_names_by_key,
                       'product_type': db.get_product_types_by_key,
                       'vendor': db.get_vendors_by_key}
            return drivers[entity_type]

        db_function = entities_function_generator(gazetteer_type)
        entities = db_function(id_)
        return entities


class GazetteerModelAccessor:
            
    def get_gazeteers(self, id_):
        """
        Get the gazetteers associated with an id
        
        Parameters
        ----------
        id_: The id that will differentiate entity lists in the database
        gazetteer_types: A list of entity list to be retrieved from the database
        
        Returns:
        --------
        gazetteers: a dict of the gazetteer types and the associated gazetteer matched to the id
        
        Exceptions
        ----------
            TODO
            
        """
        global GAZETTEERS
        gazetteers = {}

        for gazetteer in GAZETTEERS:
                gazetteers[gazetteer] = GAZETTEERS[gazetteer][id_]
        return gazetteers


class Gazetteer:
    
    def __init__(self, trie=None):
        self.trie = trie
        self.dict_builder = DictionaryBuilder()
        self.nltk_stopwords = stopwords.words('english')
        self.stemmer = PorterStemmer()
        
    def search_query(self, query, custom_stopwords=None, max_edit_distance=2):
        
        """ If a very small string, empty string, or null is passed as the query, return None """ 
        if len(query) < 2 or query == None or query == "":
            return None
        if custom_stopwords is None:
            custom_stopwords = []

        """ Create a list of the query ngrams to be searched in the Trie """
        query = self.clean_query(query).lower()
        query = [w for w in query.split(' ') if w.lower() not in custom_stopwords]
        query_grams = self.dict_builder.ngrammer(query, 2, len(query)+1)
        query_grams = sorted(query_grams, key=lambda word: len(word), reverse=True)
        tag = self._get_query_gram_tag(query_grams, max_edit_distance)
        if tag is None:
            tag = self._get_single_word_tag(query, custom_stopwords)
        return tag
    
    def _get_query_gram_tag(self, query_grams, max_edit_distance):
        
        """ Generate potential tags based on query grams searched against trie """
        tags = []
        for idx, target in enumerate(query_grams):
            """ 
            Do not search nor add to tags if the test query gram has less tokens than any tag existing in the tags list.
            This is to ensure that the large matched tag is used and to reduce search times significantly.
            The idea is that if there is a match for a long query gram, then searching smaller ngrams is unnecessary
            """
            if len(tags) == 0 or not any(len(tag[0].split(' ')) > len(target.split(' ')) for tag in tags):
                target_length = len(target.split(' '))
                results = TrieNode.search(self.trie, target, max_edit_distance)
                if len(results)>0:
                    """ Sort results by edit distance """
                    results = sorted(results, key=lambda result: result[1])
                    """ Append first result with best edit distance to tags list but not if length is shorter than target"""
                    if len(results[0][0].split(' ')) >= target_length :
                        tags.append((results[0][0], results[0][1]))
        """ sort and filter tags based on max ngram length """  
        tags = sorted(tags, key=lambda tag: len(tag[0].split()), reverse=True)
        if len(tags) != 0:
            return tags[0][0]
        else:
            return None
        
    def _get_single_word_tag(self, query, custom_stopwords):   
        """ Generate tags based on single word matches against trie """
        potential_single_words = set()
        query = [x for x in query if x.lower() not in self.nltk_stopwords or custom_stopwords]
        for word in query:
            stemmed_word = self.stemmer.stem(word)
            results = TrieNode.search(self.trie, stemmed_word, 1)
            if(len(results)>0):
                for result in results:
                    potential_single_words.add(result)
        tags = sorted(list(potential_single_words), key=lambda word: word[1])
        if len(tags) != 0:
            return tags[0][0]
        else:
            return None

    def clean_query(self, query):
        query = remove_question_mark(query)
        query = normalize_whitespace(query)
        query = dash_to_single_space(query)
        query = remove_apostrophe(query)
        return query
