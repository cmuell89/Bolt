"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
import re

def normalize_whitespace(str):
  str = re.sub(r'\s+', ' ', str)
  str = re.sub(r'\n+', ' ', str)
  return str
  
def dash_to_single_space(str):
    return str.replace(" - ")

def remove_apostrophe(str):
    return str.replace("\'", "")