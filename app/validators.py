from webargs import ValidationError

"""
Header Validators
"""
def valid_application_type(contentType, val):
    if val == contentType:
        return True
    else:
        raise ValidationError("Unsupported media type. Currently the API only accepts 'application/json'.", 415)


"""
Custom Validators
"""
# Validate classifier passed via query
def list_of_strings(list):
    if (all((isinstance(val, str) and len(val)>0) for val in list)) and len(list)>0:
        return True
    else:
        raise ValidationError("List provided to route is malformed. Must be an non-empty array of string values each with length > 1.", 400)

