'''
Created on May 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
'''
import json

from spacy.en import English


#########################
# FUNCTIONS DEFINITIONS #
#########################
# Function that returns an array of arrays of training data. First array element is the array of training documents, the second is the labels.
def create_training_data_from_JSON(fileAddress):
	file = open(fileAddress)
	data = json.load(file)
	intents = data["intents"]
	docs = []
	labels = []
	for intent in intents:
		docs = docs + intent["expressions"]
		for i in range(len(intent["expressions"])):
			labels.append(intent["name"])
	return [docs,labels]

def dependency_labels_to_root(token):
# ''Walk up the syntactic tree, collecting the arc labels.'''
	dep_labels = []
	while token.head is not token:
		dep_labels.append(token.dep)
		token = token.head
	return dep_labels

##########
# SCRIPT #
##########

#parser
parser = English()

# Extract 
trainingData = create_training_data_from_JSON("../intents.json");
train = trainingData[0]

# Parse
parsedDocs =  [parser(x) for x in train]
labelsTrain = trainingData[1]

	
# sents = [];
# for doc in parsedDocs:
# 	print(doc)
# 	for chunk in doc.noun_chunks:
# 		print(chunk.label_, chunk.orth_, '<--', chunk.root.head.orth_)
# 	for token in doc:
# 		print(token.orth_, '-->',token.pos_)
# 	print(doc.ents)
# 	print()
# 	print()

print(parsedDocs[0])
print(parsedDocs[450])
print(parsedDocs[0].similarity(parsedDocs[450]))



############################################################
# METHOD TO CREATE POS TAG PRIOR TO CALLING PARSER.        #
# TAG PARTS OF SPEECH AFTER PROGRAMATICALLY LABELED NERS   #
############################################################

# Tokenize a string into a Doc, but don't apply the whole pipeline ---
# that is, don't predict the part-of-speech tags, syntactic parse, named
# entities, etc.

# Based on CLEAR DEPENDENCY ANNOTATIONS. See page 16 of http://www.mathcs.emory.edu/~choi/doc/clear-dependency-2012.pdf


#parser.tagger.tag_from_strings(doc, [u""])
# Now predict dependency parse and named entities. Note that if you assign
# tags in a way that's very unlike the behaviour of the POS tagger model,
# the subsequent models may perform worse. These models use the POS tags
# as features, so if you give them unexpected tags, you may be giving them
# run-time conditions that don't resemble the training data.

# test
query = 'some string'
while(query != '0'):
	query = input('Enter query: ')
	doc = parser(query)
	for chunk in doc.noun_chunks:
		print()
		print(chunk.label_, chunk.orth_, '<--', chunk.root.head.orth_)
	
	print()
	
	for token in doc:
		print(token.orth_, " --> ", token.pos_)
		print(token.ent_type_)
		
	print()




















