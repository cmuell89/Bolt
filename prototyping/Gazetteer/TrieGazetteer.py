import re
import json
import jellyfish
import sys
import timeit
from nltk.corpus import stopwords
from fuzzywuzzy import fuzz
from nltk import ngrams
from nltk.util import skipgrams

# STOPWORDS = stopwords.words('english')
""" Collect most frequent words based on intent expressions """ 
STOPWORDS = ['inventory','best','selling','items','many','how','what','in','are','the','stock','is','most',]
PRODUCTS = "../../resources/product_lists/productList1k.json";
MAX_COST = 1
product_file = open(PRODUCTS)
cleaned_product_file = open('../../resources/cleanedProducts.txt', "w")
PRODUCT_JSON = json.load(product_file)


"""
The Trie data structure keeps a set of words, organized with one node for
each letter. Each node has a branch for each letter that may follow it in the
set of words.
"""
class TrieNode:
    def __init__(self):
        self.word = None
        self.children = {}
        self.word_lengths = set()

    def insert(self, word):
        node = self
        word_length = len(word)
        for letter in word:
            if letter not in node.children: 
                node.children[letter] = TrieNode()
                node.children[letter].word_lengths.add(word_length)
            node = node.children[letter]

        node.word = word
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

""" Create vocab and product name lists"""
for product in PRODUCT_JSON['products']:
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


""" Read the words and n-grams into a tree """
word_trie = TrieNode()
for product in cleaned_product_names:  
    lc_word = product.lower()
    word_trie.insert(lc_word)
for n_gram in product_n_grams:
    lc_word = n_gram.lower()
    word_trie.insert(lc_word)
for skip_gram in product_skip_grams:
    lc_word = skip_gram.lower()
    word_trie.insert(lc_word)

query = ''
while(query != "exit"):

    
    INPUT = input("Enter search term\n").lower().replace("?", "")
    
    start_time = timeit.default_timer();
    """ generate query ngrams minimum of 2 and max n equal to length of # of query tokens """
    query = INPUT.split(' ')
    query = [w for w in query if w.lower() not in STOPWORDS]
    query_grams = n_gram_generator(query, 2, len(query)+1)
    print("Query grams:")
    print(query_grams)
     
    """ Generate potential tags based on query grams searched against trie """
    tags = []
    for idx, target in enumerate(query_grams):
        """ length of target """
        target_length = len(target)
        results = search(word_trie, target, MAX_COST)
        if(len(results)>0):
            """ Sort results by edit distance """
            results = sorted(results, key=lambda result: result[1])
            """ Append first result with best edit distance to tags list but not if length is shorter than target"""
            if(len(results[0][0])>=target_length):
                tags.append((idx, results[0][0]))
    """ sort and filter tags based on max ngram length """  
    tags = sorted(tags, key=lambda tag: len(tag[1].split()), reverse=True)
    
    print("Tags:")
    print(tags)
    
    if(len(tags)>0):
        max_ngram_size = len(tags[0][1].split())
#     print("Pre-filter")
#     print(tags)
    tags = [tag for tag in tags if len(tag[1].split()) == max_ngram_size]
#     print("Post-Filter")
#     print(tags)
#     
    """ Run token_set_ratio for tags against every product name """
    matched_products = set()  

       
    for product in cleaned_product_names:
        for tag in tags:
            set_ratio = fuzz.token_set_ratio(tag[1], product)
            sort_ratio = fuzz.token_sort_ratio(tag[1], product)
            if(set_ratio > 95):
                matched_products.add((product, set_ratio))
            if(sort_ratio > 95):
                matched_products.add((product, sort_ratio))
    
    
    if(len(matched_products) == 0 and len(query_grams) < 6):
        potential_single_words = set()
        print("Searching for single word matches")
        for word in query:
            for vocab_word in vocab:
                if(jellyfish.jaro_distance(word, vocab_word)>.90 and jellyfish.hamming_distance(word, vocab_word) < 2):
                    potential_single_words.add(vocab_word)
        print(potential_single_words)
        for product in cleaned_product_names:
            for word in potential_single_words:   
                set_ratio = fuzz.token_set_ratio(word, product)
                sort_ratio = fuzz.token_sort_ratio(word, product)
                if(set_ratio > 90):
                    matched_products.add((product, set_ratio))
                if(sort_ratio > 90):
                    matched_products.add((product, sort_ratio))
    
    
    matched_products = sorted(matched_products, key=lambda match: match[1])
    print("Final matches: ")
    final_list = [match for match in matched_products if (all(len(match[0]) >= len(tag[1]) for tag in tags))] 
    print(final_list)
    products_in_query = set()
    for product in final_list:
        products_in_query.add(product[0])
        
    print()
    print("Products in query: ")
    print(products_in_query)
    print(len(products_in_query))
    print("Time for search:")
    print(timeit.default_timer() - start_time)
    print()
    print()
    
    