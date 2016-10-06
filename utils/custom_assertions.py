'''
Created on Jul 27, 2016

@author: carl

Note: Methods left as camelCase to be consistent with assertion library. 
'''

class CustomAssertions():
    """
    Mixin class for creating custom assertions used in this testing module.
    """
    
    def assertListOfTuples(self, obj, typeArray):
        """
        typeArray is an array of types used for the comparison of the obj tuple.
            len(obj) == len(typeArray)
            type(obj[0]) == typeArray[0]
        """
        if not isinstance(obj, list):
            raise AssertionError("Object is not a list.")
        if not isinstance(obj[0], tuple):
            raise AssertionError("Object does not contain tuples")
        if len(obj) == 0:
            raise AssertionError("Method failed to return a populated list.")
        else:
            assert len(obj[0]) == len(typeArray)
            for idx in range(len(obj[0])):
                assert isinstance(obj[0][idx], typeArray[idx])
            
    def assertListOfString(self, obj):
        if isinstance(obj, str):
            raise AssertionError("Returned a string argument but expected a list of tuples of length 2")
        if len(obj) == 0:
            raise AssertionError("Method failed to return a populated list.")
        else:
            assert isinstance(obj[0], str)