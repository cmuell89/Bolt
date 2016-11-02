"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
import re

def remove_question_mark(string):
    return string.replace("?", "")

def normalize_whitespace(string):
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r'\n+', ' ', string)
    return string
  
def dash_to_single_space(string):
    string = string.replace(" - "," ")
    return string

def remove_apostrophe(string):
    string = string.replace("\'", "")
    return string