from ..models import Relationship

VALIDATION_FAILED_ERROR = "Validation failed."
AUTHENTICATION_REQUIRED_ERROR = "Authentication required."
DUPLICATE_PERSON_ERROR = "A person with that name already exists."

def _format_error(field, message, as_list=False):
    def _format_item(item):
        return f"'{item}' {message}"

    formatted = [
        _format_item(item)
        for item in field
    ] if isinstance(field, (list, tuple)) else _format_item(field)

    if as_list and not isinstance(formatted, list):
        return [formatted]

    return formatted

def not_found_error(data):
    return f"{data} not found."


def required_error(field, as_list=False):
    return _format_error(field, 'is required.', as_list)


def string_error(field, as_list=False):
    return _format_error(field, 'must be a string.', as_list)


def non_empty_string_error(field, as_list=False):
    return _format_error(field, 'must be a non-empty string.', as_list)


def valid_relationship_error(field, as_list=False):
    valid_relationships = [r.value for r in Relationship]
    return _format_error(field, f'must be one of {valid_relationships}', as_list)

def bool_error(field, as_list=False):
    return _format_error(field, 'must be a boolean.', as_list)
