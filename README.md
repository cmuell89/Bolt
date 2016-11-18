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

	Directory location: root_of_app/.ebextensions
	
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
  

#### Current Release Major Features 
###### (See CHANGE.md for specific version updates)

- Scikit learn based classfication
	- Scikit learn pipeline
	- training data pulled from postgres db
	- confidence metrics for classification results
- In-memory Gazetteer trie with support for string distance mathcing using the Levinshtein Damerau Algorithm
    - Stored in a global hash to be used by Annotators
- Analysis Pipeline
    - Sequences of annotator objects altering a annotation object with NLP results
- Caching of SpaCy model
- Routes
	- /classification/analyze => returns intent classification and product name matches of a given expression
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
	    - Includes entity types and stopwords
	- Expression table (join on intent_id)
	- Unlabeled Expressions
	- Archived Expressions
- Database functionality:
    - Get bot keys
    - Get entities by entity type
	- Add intent
	- Add stopwords to intent
	- Add entities to intent
	- Add expressions to intent
	- Add unlabeled expressions
	- Get all unlabeled expressions
	- Get all intents
	- Get intent stopwords
	- Get intent entities
	- Get all intent expressions
	- Get all intents and expressions
	- Delete [all] expressions from an intent
	- Delete intent via name
	- Delete unlabeled expression via ID
	- Delete intent stopwords
	- Delete intent entities
- Error Handling
	- Custom errors that raise exceptions to the route level to respond with appropriate error messages and status codes
- Logging

##### Development Notes
- latest yum package dependencies required on Amazon Linux EC2 instance. These are preinstalled on an Amazon AMI and used for deploys: 
    - postgresql94-devel.x86_64: []
    - libffi-devel.x86_64: [] 
    - gcc48.x86_64: []
    - gcc48-gfortran.x86_64: []
    - libpng-devel.x86_64: [] 
    - freetype-devel.x86_64: []
    - lapack-devel.x86_64: []
    - blas-devel.x86_64: []
    - libpng-devel.x86_64: []
    - zlib-devel.x86_64: []
    - atlas-devel.x86_64: []