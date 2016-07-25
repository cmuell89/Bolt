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
	- /classify => returns intent classification of a given expression
- Database
	- Add intent
	- delete intent
	- Get all intents
	- Get all intent expressions
	- Get all intents and expressions

#### Development TODO's

- [ ] Create route to update classification model with new expressions
	- [ ] code
	- [ ] test
- [ ] Create tests for existing routes.
- [ ] Create routes to add expressions to postgres
	- [ ] code
	- [ ] test

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