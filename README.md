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
- Caching of SpaCy model ** See deployment notes
- Routes
	- /classification/classify => returns intent classification of a given expression
	- /classification/train => trains the classifier again (hopefully after new expressions were added
	- /database/expressions/<string:intent>
		- post => add expression/s to the intent passed in the url
		- get => get expressions for the intent passed in the url
		- delete => deletes expression/s for intent passed in url.
			- json payload: 
				- param: all: True/False => delete all expressions
				- param: expressions: [type:string] => delete all expressions in the array
	- /database/intents/
		- post => Add intent passed in request payload to database
		- get => Gets all the existing intents stored in the database
		- delete => Deletes intent and all associated expressions
- Database
	- Intent table
	- Expression table (join on intent_id)
- Database functionality:
	- Add intent
	- Add expressions to intent
	- delete intent
	- Get all intents
	- Get all intent expressions
	- Get all intents and expressions
	- Delete all expressions from an intent
	- Delete intent
- Error Handling
	- Custom errors that raise exceptions to the route level to respond with appropriate error messages and status codes
- Logging
	- Start of implementation of python's native logging module to make print() go the way of the dodo bird

##### Development Notes
- latest yum package dependencies required on Amazon Linux EC2 instance (will receive deploy errors if packages cannot download): 
    postgresql94-devel.x86_64: []
    libffi-devel.x86_64: [] 
    gcc48.x86_64: []
    gcc48-gfortran.x86_64: []
    libpng-devel.x86_64: [] 
    freetype-devel.x86_64: []
    lapack-devel.x86_64: []
    blas-devel.x86_64: []
    libpng-devel.x86_64: []
    zlib-devel.x86_64: []
    atlas-devel.x86_64: []
    
- Not caching Spacy Model. Uncertain if necessary at the moment
	
#### Development TODO's

##### Not Started:
- [ ] Improve classification response to show scoring metrics if possible for LinearSVM
- [ ] Implement different classify responses based on Naive Bayes or LinearSVC
- [ ] COMMENT/DOCUMENTATION OVERHAUL => START STRONG, FINISH STRONG
- [ ] Start prototyping 'Trait' parsing
- [ ] Prototype 'Entity' parsing
	- [ ] Gazetteer (Look into Matcher
	- [ ] SpaCy NER
- [ ] Start prototyping datetime parsing

##### In-Progress:
- [ ] Test caching of Spacy Model to see if it works in production
- [ ] Setup External Postgres Database to handle Expressions
- [ ] Implement request parsing and parameter validation middleware or library-
	- Currently writing too much if/elif/else paramter checking
- [ ] Create route to rebuild classifier with new options
	- [ ] code
	- [ ] test

##### Completed:
- [x] Authentication Using simple Token based WWW-Authenticate authorization
	- Requires added 'WSGIAuthenticationpass On' to wsgi.conf file on Elastic Bek 
- [x] Allow choice between Naive Bayes and LinearSVM during construction of sk-learn pipeline
- [x] Implement config/environment files for use in configuring app.
- [x] Host Server on AWS Elastic Beanstalk
- [x] Build out logging capabilities BASIC
- [x] Create route to delete intent and make sure all expressions are deleted too
	- [x] code
	- [x] test
- [x] Create route to delete expression/s
	- [x] code
	- [x] test
- [x] Create custom exceptions for to raise up to the route level for Database Errors and Database Intput Errors
- [x] Convert all server responses to JSON format rather than HTML as standard in flask (This might be alleviated by flask-restful.
	- Implemented through the jsonify(key1=value1, key2=value2, ...) method that creates a Flask resp with passed in key/value pairs
- [x] Create route to update classification model with new expressions
	- [x] code
	- [x] test
- [x] Create routes to add expressions to postgres
	- [x] code
	- [x] test
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