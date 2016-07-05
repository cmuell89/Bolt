'''
Created on Jul 3, 2016

@author: carl
'''
import parsedatetime
from pytz import timezone
import pytz


cal = parsedatetime.Calendar()


query = '1'
while(query != '0'):
    query = input('Enter temporal phrase: ')
    
    nlp_datetime_obj = cal.nlp(query)
    datetime_obj, _ = cal.parseDT(datetimeString=nlp_datetime_obj[0][4], tzinfo=timezone("US/Pacific"))
        
    print(datetime_obj)
