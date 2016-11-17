###CHANGE LOG

#### Development TODO's

##### Not Started:

- [ ] Start prototyping 'Trait' parsing
- [ ] Start prototyping datetime parsing
	- In talks with maintained of SpaCy
- [ ] Expand gazetteer beyond prodiuct names to include types, vendors, colors etc,.

##### In-Progress:
- [ ] COMMENT/DOCUMENTATION OVERHAUL => START STRONG, FINISH STRONG
- [ ] Create gazetteer
	- [x] code
	- [ ] test
- [ ] Create Analysis pipeline to combine classifier and gazetteer
	- [x] code
	- [ ] test
- [ ] Build out additional database methods to support entity types and stopwords associted with intents
	- [x] code
	- [ ] test
- [ ] integrate new db mmethods into Classification class, return results to be used by classification annotator
	- [x] code
	- [ ] test

##### Version Change Log:

###### Version 0.2 - Initial Version
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