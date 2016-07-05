'''
Created on Jul 3, 2016

@author: carl
'''
import dateparser


query = '1'
while(query != '0'):
    query = input('Enter temporal phrase: ')
    print(dateparser.parse(query))
    print()