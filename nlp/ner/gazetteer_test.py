from nlp.ner.gazetteer import GazetteerModelBuilder, GazetteerModelAccessor
import json


STOPWORDS = ['inventory','best','selling','items','many','how','what','in','are','the','stock','is','most', 'warehouse', 'sell', 'this', 'total', 'sales']


builder = GazetteerModelBuilder()
builder.create_new_gazetteer_model("product_names", 1234)
accessor = GazetteerModelAccessor()
gazetteers = accessor.get_gazzeteers(["product_names"], 1234)


query = ''
while(query != "exit"):
    query = input("Enter query:\n")
    result = gazetteers["product_names"].search_query(query, STOPWORDS, 2)
    print(result)
    print()



