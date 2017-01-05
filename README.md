# Bolt
Web Server hosting Lightning in a Bot's NLP prototype system.

## Local Python Environment
The interpreter environment is a virtual environment running Python version 3.5 (3.4 on Amazon Linux EC2 isntance).

### Local setup

The following is a guideline for setting up your local environment. Each person environment might require additional
tweaks to appropriately set up Bolt.

#### PostgreSQL
Ensure you have postgresql setup accordingly.

    sudo apt install postgresql postgresql-client postgresql-contrib libpq-dev

#### Development Dependencies
Be sure to install the following development dependencies (Debian):

    sudo apt install libffi-dev
    sudo apt install python3-dev
    sudo apt install python-psycopg2
    sudo apt install libpq-dev

#### Virtual Environment
Setup up your viritual environment using your systems python3, at least python 3.4.

    sudo apt install virutalenv
    cd $local/bolt/directory
    virtualenv -p python3 bolt-env

Activate using

    source $(TopLevelBoltDirectory)/bolt-env/bin/activate

#### Python packages
See requirements.txt for dependency requirements.
Activate virtual environment, then

      pip install -r requirements.txt
  
Additional dependencies may be required for individual packages required by Bolt.

#### Language Models
Make sure to activate virtual environment then install the following language models.
  - python -m spacy.en.download
Run nltk downloader
  - python
  - import nltk
  - nltk.downloader()
  - Follow instructions to download 'stopwords'


## Deploy Requirements
Deploying onto Elastic Beanstalk requires the CLI tool eb (you can also use the more general aws CLI tool)

### New Version Deployment
When deploying new versions of Bolt from the CLI locally to production create a test environment on 
Elastic Beanstalk first! 

#### Blue Green Deployment

1. Enter current environment.
2. Clone environment labeling it as blue or green (will depend on previous release)
3. Enter NEW environment
4. Deploy new app version to NEW environment.
5. Test, test, test
6. Swap environment URLs from old environment.
7. Delete old environment (or shutdown via EC2 console)


#### Deployment steps
To configure the current Bolt version to deploy to the test environment, run:

    eb init 

Additionally, make sure to create the following file (ensure proper .yml format 2 space indents!):

Directory location: 
   
    root_of_Bolt_app/.ebextensions/02_environment.config

Contents:

    option_settings:
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: ENVIRONMENT
        value: prod
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: NLP_SCHEMA
        value: nlp
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: ACCESS_TOKEN
        value: your_access_token
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: BOLT_DB_NAME
        value: dbname
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: BOLT_HOSTNAME
        value: dbHostEndpoint
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: BOLT_DB_PORT
        value: port
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: BOLT_DB_USERNAME
        value: username
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: BOLT_DB_PASSWORD
        value: password
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: PAPERTRAILS_ADDRESS
        value: papertrails_address
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: PAPERTRAILS_PORT
        value: papertrails_port
      - namespace: aws:elasticbeanstalk:application:environment
        option_name: SECRET_KEY
        value: secret_key
  

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
    - Currently uses two pipelines
        - The first is the initial classification
        - The second is constructed with annotators that only exist in the entity_type results from the first annotator pipeline
- Caching of SpaCy model
- Routes
	- /nlp/analyze => returns intent classification and product name matches of a given expression
	- /nlp/train
	    - post => trains specific models (multiclass, binary classifier, gazetteer) (hopefully after new expressions were added
	        - json payload:
	            - param: all: True/False => train all models or piecemeal
	            - param: multiclass
	                - all: True/False => train all multiclass models or if false, must provide name
	                - name: name of multiclass classifier to train
	            - param: binary_classifier
	                - all: True/False => train all binary_classifier models or if false, must provide name
	                - name: name of binary_classifier classifier to train
	            - param: gazetteer
	                - all: True/False => train all multiclass models or if false, must provide key
	                - key: bot key of gazetteer model to train
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
	- Unlabeled Expressions
	- Archived Expressions
	- Entities_Expressions m:n linkage table
	- Intents_Entities m:n linkage table
	- Entities Table
- Database functionality:
    - Get bot keys
    - Get entities by entity type
	- Add intent
	- Add stopwords to intent
	- Add entities to intent
	- Add expressions to intent
	- Add unlabeled expressions
	- Add entity
	- Add binary_classifier entity link to expression
	- Get all unlabeled expressions
	- Get all intents
	- Get intent stopwords
	- Get intent entities
	- Get all intent expressions
	- Get all intents and expressions
	- Get all binary_classifier expressions
	- Delete [all] expressions from an intent
	- Delete intent via name
	- Delete unlabeled expression via ID
	- Delete intent stopwords
	- Delete intent entities
	- Delete entity
	- Delete binary_classifier entity link froms expression
	
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