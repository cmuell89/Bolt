"""
Created on November 4th, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
from nltk import ngrams
from nltk.util import skipgrams
from nltk.stem.porter import PorterStemmer
from utils import string_cleaners


class GramTrieBuilder:

    def build_trie_from_dictionary(self, dictionary):
        """
        Returns the root TrieNode of a trie containing cleaned dictionary entries, and their associated
        n-grams and skipgrams
        :param dictionary: list of tokens
        :return: TrieNode reference to root
        """
        trie = TrieNode()
        dict_builder = DictionaryBuilder()
        
        cleaned_dictionary = dict_builder.clean_dictionary(dictionary)
        word_list = dict_builder.extract_vocab_from_dictionary(cleaned_dictionary, stemmed=False)
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


class SimpleTrieBuilder:

    def build_simple_trie_from_dictionary(self, dictionary):
        """
        Returns the root TrieNode of a trie containing stemmed, lower-cased, uncleaned and cleaned dictionary entries only.
        :param dictionary: list of tokens
        :return: TrieNode reference to root
        """
        trie = TrieNode()
        dict_builder = DictionaryBuilder()


        cleaned_dictionary = dict_builder.clean_dictionary(dictionary)

        stemmer = PorterStemmer()
        for entry in cleaned_dictionary:
            entry = entry.lower()
            entry = stemmer.stem(entry)
            trie.insert(entry)
        for entry in dictionary:
            entry = entry.lower()
            entry = stemmer.stem(entry)
            trie.insert(entry)
        return trie

    def build_trie_from_serialized_json(self, json_string):
        pass

    def serialize_trie_to_json(self, trie):
        pass


class DictionaryBuilder:
    
    def clean_dictionary(self, dictionary):
        """
        Cleans each entry in the dictionary and returns the altered dictionary
        :param dictionary: a list of tokens
        :return: list of cleaned tokens
        """
        cleaned_dictionary = [self._clean_dictionary_entry(entry) for entry in dictionary]
        return cleaned_dictionary
        
    def ngram_generator(self, dictionary):
        """
        Generates ngrams from size 2 to size of the number of tokens in the dictionary entry and returns the combined list
        :param dictionary: a list of tokens
        :return: a list of n-grams
        """
        n_grams = []
        results = [self.ngrammer(entry.split(' '), 2, len(entry.split(' '))) for entry in dictionary if len(entry.split(' '))>1]
        for result in results:
            n_grams.extend(result)
        return n_grams
    
    def skipgram_generator(self, dictionary):
        """
        Generates various size and skip distance skipgrams and returns the combined list
        :param dictionary: a list of tokens
        :return: a list of skipgrams
        """
        skip_grams = []
        results = [self.skipgrammer(entry.split(' '), 2, 2) for entry in dictionary]
        results.extend([self.skipgrammer(entry.split(' '), 3, 3) for entry in dictionary])
        results.extend([self.skipgrammer(entry.split(' '), 3, 2) for entry in dictionary])
        results.extend([self.skipgrammer(entry.split(' '), 2, 3) for entry in dictionary])
        for result in results:
            skip_grams.extend(result)
        return skip_grams
    
    def extract_vocab_from_dictionary(self, dictionary, stemmed=False):
        """
        Returns list of single vocab words generated from the dictionary
        :param dictionary: list of tokens
        :param stemmed: boolean determining whether to stem individual words
        :return: list of single word tokens
        """
        vocab = []
        for entry in dictionary:
            words = entry.split(' ')
            if stemmed == True:
                stemmer = PorterStemmer()
                words = [stemmer.stem(word) for word in words]
            vocab.extend(words)
        return vocab
            
        
    def ngrammer(self, span, minimum, maximum):
        """
        Returns list of token n-grams of length 'minimum' to length 'maximum' on the provided span of tokens
        :param span: a set of tokens as a single string.
        :param minimum: minimum length of n-gram
        :param maximum: maximum length of n-gram
        :return: lsit of n-grams
        """
        n_grams = []
        for n in range(minimum, maximum):
            for ngram in ngrams(span, n):
                n_grams.append(' '.join(str(i) for i in ngram))

        return n_grams
    
    def skipgrammer(self, span, n, k):
        """
        Returns list of token skip-grams of size n with skip distance k on the provided span of tokens
        :param span: a set of tokens as a single string.
        :param n: the size or number of tokens of generated skipgrams
        :param k:the skip distance
        :return: listof skipgrams
        """
        skip_grams = []
        grams = list(skipgrams(span, n, k))
        for g in grams:
            skip_grams.append(' '.join(str(i) for i in g))
        return skip_grams
    
    def _clean_dictionary_entry(self, entry):
        """
        Cleans the entry string using series of string processing functions
        :param entry: string to be cleaned
        :return: cleaned string
        """
        entry = string_cleaners.normalize_whitespace(entry)
        entry = string_cleaners.dash_to_single_space(entry)
        entry = string_cleaners.remove_apostrophe(entry)
        entry = string_cleaners.remove_foward_slash(entry)
        entry = string_cleaners.remove_commas(entry)
        entry = string_cleaners.remove_quotations(entry)
        return entry


class TrieNode(dict):
    
    def __init__(self, word=None, children=None, word_lengths=None):
        super().__init__()
        self.__dict__ = self
        self.word = None if not word else word
        self.children = {} if not children else children

    def insert(self, word):
        """
        Inserts a word into the the trie letter by letter
        :param word: word to be inserted
        """
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
        :param trie: root TrieNode on which to conduct the search
        :param word: string to search
        :param maxCost: max edit distance allowed for during running of search algorithm
        :return: returns a list of tuples containing word and edit distance
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
    def search_recursive(node, letter, word, previous_row, results, max_cost):
        """
        This recursive search function that performs Levenshtein distance as adapted from
        http://stevehanov.ca/blog/index.php?id=114
        This algorithm recursively calculates the Levenshtein distance via a comparison matrix, succesively adding
        the next letter in a search path of the trie. This calculates the edit distances of the new word comparison by
        calculating only an additional row.
        :param node: the current TrieNode
        :param letter: current letter of row
        :param word: current word being searched
        :param previous_row: previous row from previous recursive call
        :param results: array of results passed along the recursion
        :param max_cost: maximum edit distance of the Levenshtein edit distance algorithm
        """
        columns = len(word) + 1
        current_row = [previous_row[0] + 1]
    
        """ 
        Build one row for the letter, with a column for each letter in 
        the target word, plus one for the empty string at column 0
        """
        for column in range(1, columns):
    
            insert_cost = current_row[column - 1] + 1
            delete_cost = previous_row[column] + 1
    
            if word[column - 1] != letter:
                replace_cost = previous_row[column - 1] + 1
            else:
                replace_cost = previous_row[column - 1]

            current_row.append(min(insert_cost, delete_cost, replace_cost))
    
        # if the last entry in the row indicates the optimal cost is less than the
        # maximum cost, and there is a word in this trie node, then add it.
        if current_row[-1] <= max_cost and node.word is not None:
            results.append((node.word, current_row[-1]))
    
        # if any entries in the row are less than the maximum cost, then 
        # recursively search each branch of the trie
        if min(current_row) <= max_cost:
            for letter in node.children:
                TrieNode.search_recursive(node.children[letter], letter, word, current_row, results, max_cost)
