# Bolt
Web Server hosting Lightning in a Bot's NLP prototype system.

### Python Environment
The interpreter environment is Anaconda3 with Python version 3.5.

### Build Requirements
See requirements.txt for dependency requirements.
Packages can be installed via the conda package manager or pip.
Additional dependencies may be required for individual packages required by Bolt

#### Current Release Features
- Scikit learn classification pipeline training and use
- Caching of SpaCy model
- Route that returns intent of given query (returns name of intent only)

#### Development TODO's
- [x] Create table 'intent_expressions', in schema 'nlp', in local server database 'test'
- [ ] Update training of classifier to use intents/expressions in postgres
	- [ ] code
	- [ ] test
- [ ] Create routes to add expressions to postgres
	- [ ] code
	- [ ] test
- [ ] Create route to update classification model with new expressions
	- [ ] code
	- [ ] test