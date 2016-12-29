from webargs import ValidationError

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


def validate_binary_classifier_parameters(parameters):
    if isinstance(parameters, dict):
        if 'all' not in parameters.keys():
            raise ValidationError("Parameters must have 'all' key!", 400)
        elif parameters['all'] not in [True, False, 'true', 'false', 1, 0]:
            raise ValidationError("The 'all' parameter must be a valid boolean", 400)
        elif parameters['all'] in [False, 'false', 0]:
            if 'name' not in parameters.keys():
                raise ValidationError("Parameters must have 'name' key if not training all binary_classifiers!", 400)
    else:
        raise ValidationError("Must be a valid JSON/dict object", 400)


def validate_multiclass_parameters(parameters):
    if isinstance(parameters, dict):
        if 'all' not in parameters.keys():
            raise ValidationError("Parameters must have 'all' key!", 400)
        elif parameters['all'] not in [True, False, 'true', 'false', 1, 0]:
            raise ValidationError("The 'all' parameter must be a valid boolean", 400)
        elif parameters['all'] in [False, 'false', 0]:
            if 'name' not in parameters.keys():
                raise ValidationError("Parameters must have 'name' key if not training all binary_classifiers!", 400)
    else:
        raise ValidationError("Must be a valid JSON/dict object", 400)


def validate_gazetteer_parameters(parameters):
    if isinstance(parameters, dict):
        if 'all' not in parameters.keys():
            raise ValidationError("'gazetteer' must have 'all' key!", 400)
        elif parameters['all'] not in [True, False, 'true', 'false', 1, 0]:
            raise ValidationError("The 'all' parameter must be a valid boolean", 400)
        elif parameters['all'] in [False, 'false', 0]:
            if 'key' not in parameters.keys():
                raise ValidationError("Parameters must have 'key' key if not training all binary_classifiers!", 400)
    else:
        raise ValidationError("Must be a valid JSON/dict object", 400)