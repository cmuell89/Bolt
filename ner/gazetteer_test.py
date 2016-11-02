from ner.gazetteer import TrieBuilder, TagSearcher
import json

file_name = "../resources/product_lists/productList.json";
product_file = open(file_name)
product_json = json.load(product_file)
products = product_json['products']
STOPWORDS = ['inventory','best','selling','items','many','how','what','in','are','the','stock','is','most', 'warehouse', 'sell', 'this']

builder = TrieBuilder()
tagger = TagSearcher()

trie = builder.build_trie_from_dictionary(products)
query = ''
while(query != "exit"):
    query = input("Enter query:\n")
    result = tagger.get_tag(trie, query, STOPWORDS, 2)
    print(result)
    print()



