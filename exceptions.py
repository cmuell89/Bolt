'''
Created on Aug 10, 2016

@author: carl
'''

class DatabaseError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class DatabaseInputError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value) 