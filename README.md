# Bolt
Web Server hosting Lightning in a Bot's NLP prototype system.

### Python Environment
The interpreter environment is Anaconda3 with Python version 3.5.

### Build Requirements
See requirements.txt for dependency requirements.
Packages can be installed via the conda package manager or pip.
Additional dependencies may be required for individual packages required by Bolt

#### Current Release Features
- Scikit learn based classfication
	- Scikit learn pipeline
	- training data pulled from postgres db
- Caching of SpaCy model
- Routes
	- /classification/classify => returns intent classification of a given expression
- Database
	- Intent table
	- Expression table (join on intent_id)
- Database functionality:
	- Add intent
	- delete intent
	- Get all intents
	- Get all intent expressions
	- Get all intents and expressions
	- Delete all expressions from an intent
	- Delete intent

#### Development TODO's

##### Not Started:


- [ ] Create route to update classification model with new expressions
	- [ ] code
	- [ ] test
- [ ] Create routes to add expressions to postgres
	- [ ] code
	- [ ] test

##### In-Progress:
- [ ] Convert all server responses to JSON format rather than HTML as standard in flask (This might be alleviated by flask-restful. Exploring

##### Completed:

- [x] Explore potential use of Flask Restful extension rather than using smaller basic extensions (reinventing wheel?)
- [x] Create tests for existing routes.
- [x] Create database method to remove all expressions from an intent
	- [x] code
	- [x] test
- [x] Create database methods to add and remove an intent
	- [x] code
	- [x] test 
- [x] Create table 'intent_expressions', in schema 'nlp', in local server database 'test'
- [x] NLP_Database class to pull intents and expressiosn from pg database
	- [x] code
	- [x] test
- [x] Update training of classifier to use intents/expressions in postgres
	- [x] code
	- [x] test
- [x] Initial push to git:
	- Basic classification module
	- Transformers
	- caching of Spacy model
	- basic Flask app
	- resources