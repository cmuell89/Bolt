'''
Created on Oct 14, 2016

@author: carl
'''
import settings
import json
from nlp.ner.gazetteer import SimpleTrieBuilder, SimpleGazetteer, Gazetteer, GramTrieBuilder


product_types = []
with open('../../resources/product_lists/product_types.json') as f:
    file_data = json.load(f)
    for product_type in file_data['product_types']:
        print(product_type)
        product_types.append(product_type)

trie_builder = SimpleTrieBuilder()
trie = trie_builder.build_simple_trie_from_dictionary(product_types)

gazetteer = Gazetteer(trie)

query = ""
while query != 'exit':
    query = input("Test query: ")
    results = gazetteer.search_query(query, ['what', 'are', 'best', 'selling'])
    print(results)
