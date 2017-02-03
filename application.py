"""
Created on Jul 18, 2016

@author: carl
"""
import settings
import os
from app import application

# run the app according to the ENVIRONMENT env variable.
if __name__ == "__main__": 
    if os.environ.get('ENVIRONMENT') == 'dev':
        application.run(host=os.environ.get('DEV_HOST'), port=int(os.environ.get('DEV_PORT')),
                        debug=True, use_reloader=False)
    elif os.environ.get('ENVIRONMENT') == 'test':
        application.run(debug=False, use_reloader=False)
    elif os.environ.get('ENVIRONMENT') == 'prod':
        application.run()