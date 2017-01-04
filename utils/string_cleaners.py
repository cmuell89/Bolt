"""
Created on October 26, 2016

@author: Carl L. Mueller
@copyright: Lightning in a Bot, Inc
"""
import re


def remove_commas(string):
    string = string.replace(",", "")
    return string


def remove_foward_slash(string):
    string = string.replace(" / ", " ")
    string = re.sub(r'(?<=[a-zA-Z0-9])/(?=[a-zA-Z0-9])', ' ', string)
    return string


def remove_question_mark(string):
    string = string.replace("?", "")
    return string


def normalize_whitespace(string):
    string = re.sub(r'\s+', ' ', string)
    string = re.sub(r'\n+', ' ', string)
    return string


def dash_to_single_space(string):
    string = string.replace(" - ", " ")
    return string


def remove_apostrophe(string):
    string = string.replace("\'", "")
    return string


def remove_quotations(string):
    string = string.replace('\"', '')
    return string
