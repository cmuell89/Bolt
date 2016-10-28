'''
Created on Oct 17, 2016

@author: carl
'''
import json
import re
import timeit
import sys
import zlib
from nltk import ngrams
from nltk.util import skipgrams

PRODUCT_FILE = "../../resources/product_lists/productListSingles.json";
MAX_COST = 1
PRODUCTS = json.load(open(PRODUCT_FILE))

print("Size of product list:")
print(sys.getsizeof(PRODUCTS['products'])/1000000)
print()

SIZE = 0;

"""
The Trie data structure keeps a set of words, organized with one node for
each letter. Each node has a branch for each letter that may follow it in the
set of words.
"""
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
"""
The search function returns a list of all words that are less than the given
maximum distance from the target  using the provided TrieTrie
"""
def search(trie, word, maxCost):

    # build first row
    currentRow = range(len(word) + 1)

    results = []

    # recursively search each branch of the trie
    for letter in trie.children:
        search_recursive(trie.children[letter], letter, word, currentRow, 
            results, maxCost)

    return results

"""
This recursive helper is used by the search function above. It assumes that
the previousRow has been filled in already.
"""
def search_recursive(node, letter, word, previousRow, results, maxCost):

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
            search_recursive( node.children[letter], letter, word, currentRow, 
                results, maxCost ) 
        
def n_gram_generator(words, minimum, maximum):
    s = []
    for n in range(minimum, maximum):
        for ngram in ngrams(words, n):
            s.append(' '.join(str(i) for i in ngram))
    return s

def skip_gram_generator(iterable, n, k):
    s = []
    grams = list(skipgrams(iterable, n, k))
    for g in grams:
        s.append(' '.join(str(i) for i in g))
    return s

product_names = []
cleaned_product_names = []
vocab = []

start_time = timeit.default_timer()   
""" Create vocab and product name lists"""
for product in PRODUCTS['products']:
    product_names.append(product)
    cleaned_product = re.sub(r'\s+', ' ', product).replace("\'", "").replace(" - "," ").lower()
    cleaned_product_names.append(cleaned_product)
    words = cleaned_product.split(' ')
    vocab.extend(words)


""" Create ngrams of products """
product_n_grams = []
for product in cleaned_product_names:
    product = product.split()
    n_grams = n_gram_generator(product, 2, len(product))
    product_n_grams.extend(n_grams)
    
""" Create skipgrams of products """
product_skip_grams = []
for product in cleaned_product_names:
    product = product.split()
    skip_grams = skip_gram_generator(product, 3, 2)
    product_skip_grams.extend(skip_grams)
    skip_grams = skip_gram_generator(product, 3, 3)
    product_skip_grams.extend(skip_grams)
    skip_grams = skip_gram_generator(product, 2, 2)
    product_skip_grams.extend(skip_grams)
    skip_grams = skip_gram_generator(product, 2, 3)
    product_skip_grams.extend(skip_grams)

 
trie = TrieNode()

""" Read the words and n-grams into a tree """
for product in cleaned_product_names:  
    lc_word = product.lower()
    trie.insert(lc_word)
for n_gram in product_n_grams:
    lc_word = n_gram.lower()
    trie.insert(lc_word)
for skip_gram in product_skip_grams:
    lc_word = skip_gram.lower()
    trie.insert(lc_word)
 
trie_build_time = timeit.default_timer() - start_time

print("Search for 'distressed bel air' after normal build:")
start_search = timeit.default_timer()
print(search(trie, 'distressed bel air', 1))
print()

search_time_normal = timeit.default_timer() - start_search    
print("Search time:")
print(search_time_normal)
print()

print("Normal build time (includes all string processing):")
print(trie_build_time)
print()

start_save_time = timeit.default_timer()
json_str = json.dumps(trie, sort_keys=True)
compressed_json_str = zlib.compress(json_str.encode('utf-8'))
print("Save time:")
print(timeit.default_timer() - start_save_time)
print()

print("Size of uncompressed serialized json:")
print(sys.getsizeof(json_str)/1000000)
print()

print("Size of compressed serialized json:")
print(sys.getsizeof(compressed_json_str)/1000000)
print()

start_time = timeit.default_timer()
decompressed_json_str = zlib.decompress(compressed_json_str)
rebuilt_trie = TrieNode.from_dict(json.loads(decompressed_json_str.decode('utf-8')))
trie_reconstruction_time = timeit.default_timer() - start_time


print("Search for ''distressed bel air' after reconstruction from json string:")
start_search = timeit.default_timer()
print(search(rebuilt_trie, 'distressed bel air', 1))   
search_time_reconstructed = timeit.default_timer() - start_search 

print()
print("Search time:")
print(search_time_reconstructed)
    
print()
print("Reconstruction build time:")
print(trie_reconstruction_time)

    

    
    