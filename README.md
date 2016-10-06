# Bolt
Web Server hosting Lightning in a Bot's NLP prototype system.

### Python Environment
The interpreter environment is a virtual environment running Python version 3.5 (3.4 on Amazon Linux EC2 isntance).

### Build Requirements
See requirements.txt for dependency requirements. 
Be sure to install in your virtual environment via $ pip install -r requirements.txt.
Additional dependencies may be required for individual packages required by Bolt.

### Deploy Requirements
Deploying onto Elastic Beanstalk requires the CLI tool eb (you can also use the more general aws CLI tool)

When deploying from the CLI locally to production create a test environment on Elastic Beanstalk first! 

Run eb init to configure the current Bolt version to deploy to the test environment.

Additionally, make sure to create the following file (ensure proper .yml format 2 space indents!):

	Directory location: .elasticbeanstalk
	
	Filename: 01_environment.config
	
	Contents:
	
	option_settings:
  	  - namespace: aws:elasticbeanstalk:application:environment
        option_name: ENVIRONMENT
        value: prod
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: ACCESS_TOKEN
        value: your_access_token
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: RDS_DB_NAME
        value: dbname
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: RDS_HOSTNAME
        value: dbHostEndpoint
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: RDS_PORT
        value: port
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: RDS_USERNAME
        value: username
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: RDS_PASSWORD
        value: password
  

#### Current Release Features
- Scikit learn based classfication
	- Scikit learn pipeline
	- training data pulled from postgres db
	- confidence metrics for classification results
- Caching of SpaCy model
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
	- /aws-eb-health
		- health test for Elastic Beanstalk
- Database
	- Intent table
	- Expression table (join on intent_id)
	- Unalabeled Expressions
- Database functionality:
	- Add intent
	- Add expressions to intent
	- Add unlabeled expressions
	- Get all unlabeled expressions
	- Get all intents
	- Get all intent expressions
	- Get all intents and expressions
	- Delete [all] expressions from an intent
	- Delete intent via name
	- Delete unlabeled expression via ID
- Error Handling
	- Custom errors that raise exceptions to the route level to respond with appropriate error messages and status codes
- Logging

##### Development Notes
- latest yum package dependencies required on Amazon Linux EC2 instance. These are preinstalled on an Amazon AMI and used for deploys: 
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
	
#### Development TODO's

##### Not Started:

- [ ]
- [ ] COMMENT/DOCUMENTATION OVERHAUL => START STRONG, FINISH STRONG
- [ ] Start prototyping 'Trait' parsing
- [ ] Start prototyping datetime parsing
	- Hit up SpaCy's gitter to see if we can make this into a 
- [ ] Implement different classify responses based on Naive Bayes or LinearSVC
- [ ] Create route to rebuild classifier with new options
	- [ ] code
	- [ ] test

##### In-Progress:
- [ ] Look into using Flask's g object for persistent db connection to assist with thread safety
	- no g, no db 
	- perhaps switch to sql-alchemy which manages db connections internally
	- http://kronosapiens.github.io/blog/2014/08/14/understanding-contexts-in-flask.html
- [ ] Create basic validation webpage for unlabeled expressions.
	- [ ] code
	- [ ] test
- [ ] 
- [ ] Prototype 'Entity' parsing
	- [ ] Gazetteer (Look into Matcher
		- Indexing techniques??
	- [ ] SpaCy NER


##### Completed:
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