import settings
from nlp.ner.number_parser import NumberExtractor


numberParser = NumberExtractor()
numberParser.matcherBuilder()

query = 'some string'
while(query != '0'):
    query = input('Enter query: ')
    print(numberParser.parse(query))
