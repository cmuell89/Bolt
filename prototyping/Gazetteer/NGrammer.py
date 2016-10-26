import re
from fuzzywuzzy import fuzz
from nltk import ngrams

PRODUCTS = "../../resources/productList6k.txt";

f = open(PRODUCTS, "rt")
product_names = []
cleaned_product_names = []
vocab = []

""" Create vocab and product name lists"""
for line in f:
    new_line = line.replace("\"", "").replace(",", "").replace("\n", "").replace("\'", "")
    new_line = re.sub(r'\s+', ' ', new_line).strip()
    product_names.append(new_line)
    new_line = new_line.replace(" - "," ").replace("&","")
    cleaned_product_names.append(new_line)
    words = new_line.split(' ')
    vocab.extend(words)

product_name_n_grams = []
for product in cleaned_product_names:
    product = product.split()
    product_bigrams = [tup[0]+ " " + tup[1] for tup in list(ngrams(product, 2))]
    product_trigrams = [tup[0]+ " " + tup[1] + " " + tup[2] for tup in list(ngrams(product, 3))]
    product_name_n_grams.extend(product_bigrams)
    product_name_n_grams.extend(product_trigrams)

master_list = cleaned_product_names + product_name_n_grams

query = ''
while(query != "exit"):
    query = input("Query please: \n").replace("?", "")

    results = set()
    for product in master_list:
        ratio_uppercase = fuzz.partial_ratio(product, query)
        ratio_lowercase = fuzz.partial_ratio(product.lower(), query)
        # print(product, ratio_uppercase, ratio_lowercase)
        if (ratio_uppercase > 90):
            results.add()((product, ratio_uppercase))
        if (ratio_lowercase > 90):
            results.add((product, ratio_lowercase))
       
    products_in_query = set()     
    for product in product_names:
        if len(results) > 0:
            for result in results:
                ratio = fuzz.token_set_ratio(result[0], product)
                if(ratio > 50):
                    products_in_query.add((product, ratio))
    
    print("Master List Matches: ")         
    print(results)
    print()
    print("Products in query: ")
    print(products_in_query)
    print()