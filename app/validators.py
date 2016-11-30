from webargs import ValidationError
from database.database import ExternalDatabaseEngine
"""
Header Validators
"""
def valid_application_type(content_type, val):
    """
    Confirm that val is the equal to the provided content type.
    :param content_type: the content type required by this validation method
    :param val: The value of the content type to be validated from the request
    :return: True or validation error if validation fails.
    """
    if val == content_type:
        return True
    else:
        raise ValidationError("Unsupported media type. Currently the API only accepts 'application/json'.", 415)

"""
Custom Validators
"""
def list_of_strings(list):
    """
    Validate a list is a list of strings
    :param list: the list to be validated
    :return: True or validation error if validation fails.
    """
    if (all((isinstance(val, str) and len(val)>0) for val in list)) and len(list)>0:
        return True
    else:
        raise ValidationError("List provided to route is malformed. Must be an non-empty array of string values each with length > 1.", 400)