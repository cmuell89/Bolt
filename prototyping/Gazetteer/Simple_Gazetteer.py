'''
Created on Oct 14, 2016

@author: carl
'''
import re

product_types = []
with open('../../resources/product_types.json') as f:
    for line in f:
        product_types.append(line)



""" Create vocab and product name lists"""
for line in f:
    new_line = line.replace("\"", "").replace(",", "").replace("\n", "").replace("\'", "").replace(" - "," ")
    new_line = re.sub(r'\s+', ' ', new_line).strip()
    product_names.append(new_line)
    new_line = new_line.replace("&","")
    cleaned_product_names.append(new_line)
    words = new_line.split(' ')
    vocab.extend(words)