# Bolt
Web Server hosting Lightning in a Bot's NLP prototype system.

## Local Python Environment
The interpreter environment is a virtual environment running Python version 3.5 (3.4 on Amazon Linux EC2 isntance).

### Local setup

The following is a guideline for setting up your local environment. Each person environment might require additional
tweaks to appropriately set up Bolt.

#### PostgreSQL
Ensure you have postgresql setup accordingly.
```
sudo apt install postgresql postgresql-client postgresql-contrib libpq-dev
```
#### Development Dependencies
Be sure to install the following development dependencies (Debian):
```
sudo apt install libffi-dev
sudo apt install python3-dev
sudo apt install python-psycopg2
```
#### Virtual Environment
Setup up your viritual environment using your system's python3 interpreter (>v3.4).
```
sudo apt install virutalenv
cd $local/bolt/directory
virtualenv -p python3 env
```
Activate using

```source pathToBolt/env/bin/activate```

#### Python packages
See requirements.txt for dependency requirements.
Activate virtual environment, then

```
pip install -r requirements.txt
```
  
Additional dependencies may be required for individual packages required by Bolt.

#### Language Modeels
First ensure that the following directory exist:

- pathToBolt/models/language/nltk_data
   
Then download SpaCy lanuage parsing model (large file, may take some time):
```
source pathToBolt/env/bin/activate
python -m spacy download en_core_web_md
```
Download NLTK stopwords data:
```
source pathToBolt/env/bin/activate
python -m nltk.downloader -d pathToBolt/models/language/nltk_data stopwords
```

##### Server configurations

`config/docker/production/bolt_nginx.conf`: 
The main nginx server configuratino for the Passenger Phusion image running nginx:
```
server {
    listen 80 default_server;
    server_name localhost;
    root /home/app/Bolt/public;
    passenger_enabled on;
    passenger_user app;
    passenger_app_env production;
    passenger_python /home/app/Bolt/env/bin/python3;
    passenger_min_instances 1;
}
```

`config/docker/production/bolt_nginx_env.conf`:
Declared environment variables to be assigned via the Elastic Beanstalk console:
```
env ENVIRONMENT;
env NLP_SCHEMA;
env ACCESS_TOKEN;
env BOLT_DB_NAME;
env BOLT_DB_HOSTNAME;
env BOLT_DB_PORT;
env BOLT_DB_USERNAME;
env BOLT_DB_PASSWORD;
env SECRET_KEY;
env PAPERTRAILS_ADDRESS;
env PAPERTRAILS_PORT;
env SPACY_DATA_PATH;
env NLTK_DATA_PATH;
```

`config/docker/production/bolt_nginx_http_directives.conf`:
nginx directives of the http block:
```
passenger_max_pool_size 1;
passenger_pre_start http://localhost;
```
`passenger_max_pool_size` limits the number of sub server application processes proxied by nginx and passeneger.
`passenger_pre_start` allows nginx to self ping and start the application.


`config/docker/production/boot.sh`: startup script that is run everytime the docker instance is restarted.
```
#!/bin/sh

dir="/home/app/Bolt"
logfile="/var/log/Bolt.log"

touch "$logfile"
chown -R app:app "$logfile"

mkdir -p /var/log/nginx/
chown -R www-data:adm /var/log/nginx/

chown -R app:app "$dir"
```
`config/docker/production/deb_install.sh`: Script that is run during docker image build. Installs any .deb packages wanted on the image.
```angular2html
#!/usr/bin/env bash

dpkg -i /home/app/Bolt/config/docker/production/deb_dir/*.deb
```
Current packages/files that should be preinstalled into the directory:
   - `remote-syslog2_0.20-beta1_amd64.deb`

###### Papertrails remote logging configuration
Bolt logs nginx error.log and access.log to Papertrails using remote-syslog2.

`config/docker/production/log_files.yml`: Used to configure remote-syslog2
```angular2html
files:
  - /var/log/nginx/access.log
  - /var/log/nginx/error.log
hostname: bolt
destination:
  host: logs4.papertrailapp.com
  port: 32540
  protocol: tls
```
`config/docker/production/logrotate.conf`: logrotate daemon configuration file
```angular2html
# see "man logrotate" for details
# rotate log files weekly
weekly
# keep 4 weeks worth of backlogs
rotate 4
# create new (empty) log files after rotating old ones
create
# uncomment this if you want your log files compressed
#compress
# RPM packages drop log rotation information into this directory
include /etc/logrotate.d
# no packages own wtmp -- we'll rotate them here
/var/log/wtmp {
    monthly
    create 0664 root utmp
    rotate 1
}   
```
`config/docker/production/logrotate_nginx.conf`: nginx lograote configuration for logrotate daemon
```angular2html
/var/log/nginx/*.log {
 weekly
 rotate 52
 compress
  missingok
  notifempty
  sharedscripts
  postrotate
      [ ! -f /var/run/nginx.pid ] || kill -USR1 `cat /var/run/nginx.pid`
  endscript
}
```

## Deploy Requirements
Bolt is now being deployed to Elastic Beanstalk using Docker. It utilizes Phusion's Passenger docker image.
As the image is a Ubuntu 16.04 image, Bolt currently deploys using Docker similar to that of a VM rather than
the more standard usage of containerization technology. The resulting image is fairly large, and while it is not ideal, it is required if using the Passenger / Ngnix image for production
deployment.

### New Version Deployment
When deploying new versions of Bolt from the CLI locally to production create a test environment on
Elastic Beanstalk first!

#### Deployment steps
After ensuring that the Docker image on Lightning in a Bot's dockerhub account is the correct version, deployment on a new Elastic Beanstalk environment uses a specific configuration file.

To build and push the docker image, ensure you are logged into LIAB's docker account, then in the top-level directory of Bolt run the following:

```
docker build -t cmuell89/bolt:[blue or green] .
docker push cmuell89/bolt:[blue or green]
```
Note that you will be creating a docker image called `cmuell89/bolt:blue` or `cmuell89/bolt:green`.

Create (if it does not exist) the file `Dockerrun.aws.json` with the below contents in the top level of your Bolt directory structure:

```
{
 "AWSEBDockerrunVersion": "1",
 "Authentication": {
   "Bucket": "bolt-docker-bucket",
   "Key": ".dockercfg"
 },
 "Image": {
    "Name": "cmuell89/bolt:[blue or green]",
    "Update": "true"
  },
 "Ports": [
   {
     "ContainerPort": "80"
   }
 ],
 "Logging": "/var/log/nginx"
}
```
Note that you are referencing the recently pushed docker image `cmuell89/bolt:blue` or `cmuell89/bolt:green` in the `Dockerrun.aws.json` file.

#### Blue-Green Deployment
1. When deploying a new Elastic Beanstalk server, please name the Elastic Beanstalk server environment accoriding to the blue or green deployment i.e. `bolt-green` or `bolt-blue`.
2. make sure to choose 'generic single docker' Elastic Beanstalk server platform. 
3. Choose t4-medium EC2 instance and allow for 16gb of hard drive space.
3. As the source for you application, choose to `Upload your own` and be sure to choose the Dockerrun.aws.json file.
4. The deploy will fail initially as you have to add your environment variables to the configuration using the Elastic Beanstalk UI from the previous deployed environment or emulating your .env file.
5. Switch environment over to https in the `configuration` tab listening on port 443 using the SSL certficate ID `lightninginabot.com`.
6. Once new environment is stable (healthy), swap environment URLS.
7. Test that new environment can be reached via https.
8. Terminate old environment.

####Troubleshooting
Bolt's docker images, despite the smaller SpaCy language model, are still quite large. 500-600mb as of the current version. This is due to the saving of language models in the application directory structure. 

1) Re-deployment faile:
    - Re-deploying a new version over an currently deployed container in an AWS environment can sometimes result in failure. If this is the case, try emplying a blue-green style of deployment (which you probably should be doing anyways).



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
    - Annotators
        - Gazeeteer
        - Datetime (jPype to Duckling jar)
        - number parsing
        - regex based pasring
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
	- /database/unlabeled_expressions
	    - post => Add unlabeled epxression
		- get => Gets all unlabeled_expressions
		- delete => Deletes expression by id
	- /database/archived_expressions
	    - post => Add archived epxression
		- get => Gets all archived_expressions
		- delete => Deletes expression by id
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