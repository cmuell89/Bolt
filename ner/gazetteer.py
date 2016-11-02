"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
from nltk import ngrams
from nltk.corpus import stopwords
from nltk.util import skipgrams
from nltk.stem.porter import PorterStemmer
from utils import string_cleaners

class TrieBuilder:
    """
    Returns the root TrieNode of a trie containing all product names, n-grams and skipgrams
    """
    def build_trie_from_dictionary(self, dictionary):
        trie = TrieNode()
        dict_builder = DictionaryBuilder()
        
        cleaned_dictionary = dict_builder.clean_dictionary(dictionary)
        word_list = dict_builder.extract_vocab_from_dictionary(cleaned_dictionary)
        word_list.extend(dict_builder.ngram_generator(cleaned_dictionary))
        word_list.extend(dict_builder.skipgram_generator(cleaned_dictionary))
        
        for word in word_list:
            word = word.lower()
            trie.insert(word)
        return trie
        
    def build_trie_from_serialized_json(self, json_string):
        pass
    
    def serialize_trie_to_json(self, trie):
        pass

class DictionaryBuilder:
    
    def clean_dictionary(self, dictionary):
        """ Cleans each entry in the dictionary and returns the altered dictionary """
        dictionary = [string_cleaners.normalize_whitespace(entry) for entry in dictionary]
        dictionary = [string_cleaners.dash_to_single_space(entry) for entry in dictionary]
        dictionary = [string_cleaners.remove_apostrophe(entry) for entry in dictionary]
        return dictionary
        
    def ngram_generator(self, dictionary):
        """ Generates ngrams from size 2 to size of the number of tokens in the dictionary entry and returns the combined list """
        n_grams = []
        results = [self.ngrammer(entry.split(' '), 2, len(entry.split(' '))) for entry in dictionary if len(entry.split(' '))>1]
        for result in results:
            n_grams.extend(result)
        return n_grams
    
    def skipgram_generator(self, dictionary):
        """ Generates various size and skip distance skipgrams and returns the combined list """
        skip_grams = []
        results = [self.skipgrammer(entry.split(' '), 2, 2) for entry in dictionary]
        results.extend([self.skipgrammer(entry.split(' '), 3, 3) for entry in dictionary])
        results.extend([self.skipgrammer(entry.split(' '), 3, 2) for entry in dictionary])
        results.extend([self.skipgrammer(entry.split(' '), 2, 3) for entry in dictionary])
        for result in results:
            skip_grams.extend(result)
        return skip_grams
    
    def extract_vocab_from_dictionary(self, dictionary):
        """ Returns list of single vocab words generated from the dictionary """
        vocab = []
        for entry in dictionary:
            words = entry.split(' ')
            vocab.extend(words)
        return vocab
            
        
    def ngrammer(self, span, minimum, maximum):
        """ Returns list of token n-grams of length 'minimum' to length 'maximum' on the provided span of tokens"""
        n_grams = []
        for n in range(minimum, maximum):
            for ngram in ngrams(span, n):
                n_grams.append(' '.join(str(i) for i in ngram))

        return n_grams
    
    def skipgrammer(self, span, n, k):
        """ Returns list of token skip-grams of size n with skip distance k on the provided span of tokens"""
        skip_grams = []
        grams = list(skipgrams(span, n, k))
        for g in grams:
            skip_grams.append(' '.join(str(i) for i in g))
        return skip_grams

class TrieNode(dict):
    
    def __init__(self, word=None, children=None, word_lengths=None):
        super().__init__()
        self.__dict__ = self
        self.word = None if not word else word
        self.children = {} if not children else children

    def insert(self, word):
        node = self
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()
            node = node.children[letter]

        node.word = word
        
    @staticmethod
    def from_dict(dict_):
        """ Recursively (re)construct TreeNode-based tree from dictionary. """
        root = TrieNode(dict_['word'], dict_['children'])
        for letter in dict_['children']:
            root.children[letter] = TrieNode.from_dict(root.children[letter])
        return root
    
    @staticmethod
    def search(trie, word, maxCost):
        """
        The search function returns a list tuples containing word and edit distance.
        No edit distance will be more than maximum distance from the target using the provided TrieNode
        """
        # build first row
        currentRow = range(len(word) + 1)
    
        results = []
    
        # recursively search each branch of the trie
        for letter in trie.children:
            TrieNode.search_recursive(trie.children[letter], letter, word, currentRow, 
                results, maxCost)
    
        return results
        
   
    @staticmethod
    def search_recursive(node, letter, word, previousRow, results, maxCost):
        """
        This recursive helper is used by the search function above. It assumes that
        the previousRow has been filled in already.
        """
        columns = len(word) + 1
        currentRow = [previousRow[0] + 1]
    
        """ 
        Build one row for the letter, with a column for each letter in 
        the target word, plus one for the empty string at column 0
        """
        for column in range( 1, columns ):
    
            insertCost = currentRow[column - 1] + 1
            deleteCost = previousRow[column] + 1
    
            if word[column - 1] != letter:
                replaceCost = previousRow[column - 1] + 1
            else:                
                replaceCost = previousRow[column - 1]
    
            currentRow.append(min(insertCost, deleteCost, replaceCost))
    
        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if currentRow[-1] <= maxCost and node.word != None:
            results.append((node.word, currentRow[-1]))
    
        # if any entries in the row are less than the maximum cost, then 
        # recursively search each branch of the trie
        if min( currentRow ) <= maxCost:
            for letter in node.children:
                TrieNode.search_recursive(node.children[letter], letter, word, currentRow, 
                    results, maxCost)

class TagSearcher():
    
    def __init__(self):
        self.dict_builder = DictionaryBuilder()
        self.nltk_stopwords = stopwords.words()
        self.stemmer = PorterStemmer()
    
    def get_tag(self, trie, query, intent_stopwords, edit_cost):
        
        """ Create a list of the query ngrams to be searched in the Trie """
        query = self.clean_query(query).lower()
        query = [w for w in query.split(' ') if w.lower() not in intent_stopwords]
        query_grams = self.dict_builder.ngrammer(query, 2, len(query)+1)
        query_grams = sorted(query_grams, key=lambda word: len(word), reverse=True)
         
        """ Generate potential tags based on query grams searched against trie """
        tags = []
        for idx, target in enumerate(query_grams):
            """ 
            Do not add search nor add to tags if the test query gram has less tokens than any tag existing in the tags lis.
            This is to ensure that the large matched tag is used and to reduce search times significantly
            """
            if len(tags) == 0 or not any(len(tag[0].split(' ')) > len(target.split(' ')) for tag in tags):
                target_length = len(target.split(' '))
                results = TrieNode.search(trie, target, edit_cost)
                if len(results)>0:
                    """ Sort results by edit distance """
                    results = sorted(results, key=lambda result: result[1])
                    """ Append first result with best edit distance to tags list but not if length is shorter than target"""
                    if len(results[0][0].split(' ')) >= target_length :
                        tags.append((results[0][0], results[0][1]))
        """ sort and filter tags based on max ngram length """  
        tags = sorted(tags, key=lambda tag: len(tag[0].split()), reverse=True)
        
        """ Generate tags based on single word matches against trie """
        if len(tags)==0:
            potential_single_words = set()
            query = [x for x in query if x.lower() not in self.nltk_stopwords]
            for word in query:
                stemmed_word = self.stemmer.stem(word)
                results = TrieNode.search(trie, stemmed_word, 1)
                if(len(results)>0):
                    for result in results:
                        potential_single_words.add(result)
            potential_tags = sorted(list(potential_single_words), key=lambda word: word[1])
            if len(potential_tags) != 0:
                return potential_tags[0]
            else:
                return None
        else:
            return tags[0]

    def clean_query(self, query):
        query = string_cleaners.remove_question_mark(query)
        query = string_cleaners.normalize_whitespace(query)
        query = string_cleaners.dash_to_single_space(query)
        query = string_cleaners.remove_apostrophe(query)
        return query












                