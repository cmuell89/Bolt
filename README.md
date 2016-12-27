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

TODO: Write how to do this on Elastic Beanstalk

#### Deployment steps
To configure the current Bolt version to deploy to the test environment, run:

    eb init 

Additionally, make sure to create the following file (ensure proper .yml format 2 space indents!):

Directory location: 
   
    root_of_Bolt_app/.ebextensions/01_environment.config

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
        value: password`
  

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