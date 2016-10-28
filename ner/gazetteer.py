"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
from nltk import ngrams
from nltk.util import skipgrams
from utils import string_cleaners

class TrieBuilder():
    """
    Returns the root TrieNode of a trie containing all n-grams
    """
    def __init__(self, dictionary):
        self.dictionary = dictionary
        
       
    def build_trie_from_dictionary(self, dictionary):
        trie = TrieNode()
        dict_builder = TrieDictionaryBuilder()
        cleaned_dictionary = dict_builder.clean_dictionary(dictionary)
        word_list = dict_builder.ngram_generator(cleaned_dictionary)
        word_list.extend(dict_builder.skipgram_generator(cleaned_dictionary))
        for word in word_list:
            trie.insert(self, word)
        return trie
        
    def build_trie_from_serialized_json(self, json_string):
        pass
    
    def serialize_trie_to_json(self, trie):
        pass
       


class TrieDictionaryBuilder:
    
    def clean_dictionary(self, dictionary):
        dictionary = [string_cleaners.normalize_whitespace(word) for word in dictionary]
        dictioanry = [string_cleaners.dash_to_single_space(word) for word in dictionary]
        dictionary = [string_cleaners.remove_apostrophe(word) for word in dictionary]
        return dictionary
        
    def ngram_generator(self, dictionary):
        n_grams = []
        n_grams.extend([ngrammer(word, 2, len(word)) for word in dictionary])
        return n_grams
    
    def skipgram_generator(self, dictionary):
        skip_grams = []
        skip_grams.extent([skipgrammer(word, 2, 2) for word in dictionary])
        skip_grams.extent([skipgrammer(word, 3, 3) for word in dictionary])
        skip_grams.extent([skipgrammer(word, 3, 2) for word in dictionary])
        skip_grams.extent([skipgrammer(word, 2, 3) for word in dictionary])
        return skip_grams
        
    def ngrammer(self, word, minimum, maximum):
        """ Splits the provide word on ' ' and generates token n-grams of length 'minimum' to length 'maximum' """
        n_grams = []
        words = word.split(' ')
        for n in range(minimum, maximum):
            for ngram in ngrams(words, n):
                print(ngram)
                n_grams.append(' '.join(str(i) for i in ngram))

        return n_grams
    
    def skipgrammer(self, word, n, k):
        skip_grams = []
        grams = list(skipgrams(word, n, k))
        for g in grams:
            skip_grams.append(' '.join(str(i) for i in g))
        return skip_grams

class TrieNode(dict):
    def __init__(self, word=None, children=None):
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
        The search function returns a list of all words that are less than the given
        maximum distance from the target  using the provided TrieTrie
        """
        # build first row
        currentRow = range(len(word) + 1)
    
        results = []
    
        # recursively search each branch of the trie
        for letter in trie.children:
            search_recursive(trie.children[letter], letter, word, currentRow, 
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
    
        # Build one row for the letter, with a column for each letter in the target
        # word, plus one for the empty string at column 0
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
                search_recursive(node.children[letter], letter, word, currentRow, 
                    results, maxCost)
                