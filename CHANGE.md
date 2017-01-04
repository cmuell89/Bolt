###CHANGE LOG

#### Development TODO's

##### Not Started:

- [ ] Start prototyping datetime parsing
  - In talks with maintainer of SpaCy
  - User proposed regex based toy library
  - Perhaps create a microserver to ping Duckling.
- [ ] Create location and geographical parsing
    - Look into geograpy library
- [ ] Integrate SpaCy NER for numbers and names
- [ ] Create synonym based regex parser
- [ ] Develop annotator groups (sort of like mini pipelines)
- [ ] Create bot specific annotator capability
- [ ] Write tests for Annotators and Pipelines
- [ ] Remove choice of SVM of NB from classification buildign / training (feature is never used)

##### In-Progress:


##### Version Change Log:

###### Version 0.4: Logging, Binary Classification Annotators, Binary Regex Annotators, Update Routes, .env based schema
- [x] In app logging to Papertrails, transimission syslog of Apache to Papertrails 
- [x] COMMENT/DOCUMENTATION OVERHAUL => START STRONG, FINISH STRONG
- [x] Work on gazetteer specificity
- [x] Start prototyping 'Trait' parsing 
- [x] Create ReGex annotor capability
    - [x] Code
    - [x] Test
- [x] Build test database to mimic production database for testing.
- [x] Restructure database to support entities table and connect to intents with OIDs.
- [x] Integrate trait parsing for plurality
- [x] Store annotator information in database to avoid hardcoding parameters and data
- [x] Create custom exceptions for classifiers and gazetteers
- [x] Create test for get-stopwords-and-entities database method
    - NOTE: Method has been deprecated and removed
- [x] Add m:n table for expressions and entities to link binary entities to their expressions
- [x] Expanding Train class set of endpoints to train classifiers and gazetteers piecemeal.
    - [x] Code
    - [x] Test
- [x] Choose schema search path via environement variable 
   
###### Version 0.3: Major change for gazeteer and analysis pipeline

- [x] Create gazetteer
	- [x] code
	- [x] test
- [x] Create Analysis pipeline to combine classifier and gazetteer
	- [x] code
	- [x] test
- [x] Build out additional database methods to support entity types and stopwords associted with intents
	- [x] code
	- [x] test
- [x] integrate new db mmethods into Classification class, return results to be used by classification annotator
	- [x] code
	- [x] test

###### Version 0.2
- [x] Create basic validation webpage for unlabeled expressions.
	- [x] code
	- [x] test
- [x] Build out archive table and unlabeled expression table
- [x] Look into using Flask's g object for persistent db connection

###### Version 0.1 - Initial Version
- [x] Implement unlabeled expressions table and routes to add un-validated expressions
	- [x] code
	- [x] test
- [x] Improve classification response to show scoring metrics if possible for LinearSVM
- [x] Implement request parsing and parameter validation middleware or library-
	- Using webargs library (utilizes Marshmallow)
- [x] Setup External Postgres Database to handle Expressions
- [x] Test caching of Spacy Model to see if it works in production
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