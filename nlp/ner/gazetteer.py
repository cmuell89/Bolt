"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
import os
import logging
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from utils.string_cleaners import remove_apostrophe, normalize_whitespace, remove_question_mark, dash_to_single_space, remove_foward_slash
from database.database import ExternalDatabaseEngine
from nlp.ner.trie import GramTrieBuilder, SimpleTrieBuilder, DictionaryBuilder, TrieNode

logger = logging.getLogger('BOLT.gaz')

GAZETTEERS = {}


class GazetteerModelBuilder:
    """
    Class that provides methods to initializing and updating gazetteer models.
    """
    def initialize_gazetteer_models(self):
        """
        Builds from scratch the entire GAZETTEERS dict

        """
        logger.info('Building GAZETTEERS global dict.')
        global GAZETTEERS
        gazetteer_types = ['product-name', 'product-type', 'vendor']
        db = ExternalDatabaseEngine()
        keys = db.get_keys()
        db.release_database_connection()
        for key in keys:
            for gaz_type in gazetteer_types:
                self.create_new_gazetteer_model(gaz_type, key)
        logger.info('Completed building GAZETTEERS global dict.')

    def create_new_gazetteer_model(self, gazetteer_type, key, entity_data=None):
        """
        Creates a single gazetteer in the global dictionary GAZETTEERS
        :param gazetteer_type: the type of gazetteer. Example: product_name, product_type, vendor etc,.
        :param key: the id used to access the specific gazetteer hashed within the dictionary.
        :param entity_data: list of entity strings to use as entiy source.
        """
        global GAZETTEERS
        if entity_data and isinstance(entity_data, list):
            entities = entity_data
        else:
            entities = self._get_entities_from_external_database(gazetteer_type, key)
        entities = [x for x in entities if x is not None]
        if len(entities) > 0:
            if gazetteer_type == 'product-name':
                trie_builder = GramTrieBuilder()
                new_trie = trie_builder.build_trie_from_dictionary(entities)
            else:
                trie_builder = SimpleTrieBuilder()
                new_trie = trie_builder.build_simple_trie_from_dictionary(entities)
            new_gazetteer = Gazetteer(new_trie)

            if gazetteer_type not in GAZETTEERS:
                GAZETTEERS[gazetteer_type] = {}
                GAZETTEERS[gazetteer_type][key] = new_gazetteer
            else:
                GAZETTEERS[gazetteer_type][key] = new_gazetteer

    def update_single_gazetteer_model(self, gazetteer_type, key, entity_data=None):
        """
        Updates a single gazetteer in the global dictionary GAZETTEERS
        :param gazetteer_type:  the type of gazetteer. Example: product_name, product_type, vendor etc,.
        :param key: the key used to access the specific gazetteer hashed within the dictionary.
        """
        global GAZETTEERS
        trie_builder = GramTrieBuilder()

        logger.debug('Updating gazetteer model')
        if gazetteer_type in GAZETTEERS:
            if entity_data and isinstance(entity_data, list):
                entities = entity_data
            else:
                entities = self._get_entities_from_external_database(gazetteer_type, key)
            new_trie = trie_builder.build_trie_from_dictionary(entities)
            new_gazetteer = Gazetteer(new_trie)
            GAZETTEERS[gazetteer_type][key] = new_gazetteer

    def _get_entities_from_external_database(self, gazetteer_type, key):
        """
        Obtain the entities that will be used used to train a gazetteer model
        :param gazetteer_type: The type of entity list to be retrieved from the database
        :param key: The id that will differentiate entity lists in the database
        :return: list of entities
        """
        db = ExternalDatabaseEngine()

        def entities_function_generator(entity_type, database):
            """
            Returns a callable method that will retrieve the entities for the given entity type.
            Requires database that contains methods in the dict.
            :param entity_type: type of entities to be retrieved
            :param database: external database engine
            :return: Callable that returns the entities for the given entity type
            """
            entity_retrieval_function = {'product-name': database.get_product_names_by_key,
                                         'product-type': database.get_product_types_by_key,
                                         'vendor': database.get_vendors_by_key}
            return entity_retrieval_function[entity_type]

        db_function = entities_function_generator(gazetteer_type, db)
        entities = db_function(key)
        db.release_database_connection()
        return entities


class GazetteerModelAccessor:
    """
    Class providing methods to access gazetteer models.
    """
    def get_gazeteers(self, key):
        """
        Get all gazetteers associated with a key, usually the bot key.
        :param key: The id that will differentiate entity lists in the database
        :return: dict of gazetteers associated with the provided key. Returns None if key is not in list of keys in db.
        """
        global GAZETTEERS
        gazetteers = {}
        db = ExternalDatabaseEngine()
        keys = db.get_keys()
        db.release_database_connection()
        if os.environ.get('ENVIRONMENT') != 'test':
            if key not in keys:
                return None
        for gazetteer in GAZETTEERS:
            gazetteers[gazetteer] = GAZETTEERS[gazetteer][key]
        return gazetteers


class Gazetteer:
    """
    Gazetteer class creates objects that contain the search trie, dictionary builder stopwords and stemmer used to
    search queries.
    """
    def __init__(self, trie):
        self.trie = trie
        self.dict_builder = DictionaryBuilder()
        self.nltk_stopwords = stopwords.words('english')
        self.stemmer = PorterStemmer()
        
    def search_query(self, query, custom_stopwords=None, max_edit_distance=2):
        """
        Searches the query for tags that are found for a given edit distance in the search Trie
        :param query: Query on which to run gazetteer analysis
        :param custom_stopwords: Custom stopwords that should be ignored during gazetteer analysis.
        :param max_edit_distance: Max edit distance used for the Levenshtein Damerau algorithm.
        :return: Returns the matching subsection/ngram of the query that meets the trie search criteria
        """
        
        """ If a very small string, empty string, or null is passed as the query, return None """ 
        if len(query) < 2 or query is None or query == "":
            return None
        if custom_stopwords is None:
            custom_stopwords = []

        """ Create a list of the query ngrams to be searched in the Trie """
        query = self._clean_query(query).lower()
        query = [w for w in query.split(' ') if w.lower() not in custom_stopwords]
        query_grams = self.dict_builder.ngrammer(query, 2, len(query)+1)
        query_grams = sorted(query_grams, key=lambda word: len(word), reverse=True)
        tag = self._get_query_gram_tag(query_grams, max_edit_distance)
        """ Resort to single word searching if none of the query grams returns a tag """
        if tag is None:
            tag = self._get_single_word_tag(query, custom_stopwords)
        return tag
    
    def _get_query_gram_tag(self, query_grams, max_edit_distance):
        """
        Generate potential tags based on query grams searched against trie
        :param query_grams: set up token n-grams created from the query
        :param max_edit_distance: Max edit distance used for the Levenshtein Damerau algorithm.
        :return: Found tags, if any
        """
        tags = []
        for idx, target in enumerate(query_grams):
            """ 
            Do not search nor add to tags if the test query gram has less tokens than any tag existing in the tags list.
            This is to ensure that the largest matched tag is used and to reduce search times significantly.
            The idea is that if there is a match for a long query gram, then searching smaller ngrams is unnecessary
            """
            if len(tags) == 0 or not any(len(tag[0].split(' ')) > len(target.split(' ')) for tag in tags):
                target_length = len(target.split(' '))
                results = TrieNode.search(self.trie, target, max_edit_distance)
                if len(results) > 0:
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
        """
        Generate tags based on single word matches against trie
        :param query: The query in which to find single word matches
        :param custom_stopwords: Custom stopwords that should be ignored during gazetteer analysis.
        :return: Found tags, if any
        """
        potential_single_words = set()
        query = [x for x in query if x.lower() not in self.nltk_stopwords or custom_stopwords]
        for word in query:
            stemmed_word = self.stemmer.stem(word)
            results = TrieNode.search(self.trie, stemmed_word, 1)
            if len(results) > 0:
                for result in results:
                    potential_single_words.add(result)
        tags = sorted(list(potential_single_words), key=lambda word: word[1])
        if len(tags) != 0:
            return tags[0][0]
        else:
            return None

    def _clean_query(self, query):
        """
        Cleans the query based on a set up string cleaning functions
        :param query: query string to be cleaned
        """
        query = remove_question_mark(query)
        query = normalize_whitespace(query)
        query = dash_to_single_space(query)
        query = remove_apostrophe(query)
        query = remove_foward_slash(query)
        query = remove_question_mark(query)
        return query