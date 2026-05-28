from ..models import Relationship
from .error_messages import (
  required_error,
  string_error,
  non_empty_string_error,
  valid_relationship_error,
  bool_error,
)

def parse_bool_default(value, default_bool: bool = False) -> bool:
  return value if isinstance(value, bool) else default_bool

def parse_str(field, value, errors) -> str | None:
  if not isinstance(value, str):
    errors.append(string_error(field))
    return None
  
  value = value.strip()
  
  if value == "":
    errors.append(non_empty_string_error(field))
    return None
  
  return value
  
def parse_relationship(field, value, errors) -> Relationship | None:
  if not isinstance(value, str):
    errors.append(string_error(field))
    return None
  
  relationship_str = value.strip().lower()
  
  for relationship_type in Relationship:
    if relationship_type.value.lower() == relationship_str:
      return relationship_type
  
  errors.append(valid_relationship_error(field))
  
  return None

def parse_bool(field, value, errors):
  if not isinstance(value, bool):
    errors.append(bool_error(field))
    
  return parse_bool_default(value)

validators = {
  "name": parse_str,
  "relationship": parse_relationship,
  "prayer": parse_str,
  "has_prayed": parse_bool,
}

def validate_fields(data, required_fields=None) -> tuple[list, dict]:
  required_fields = required_fields or []
  errors = []
  parsed = {}
  
  for field in required_fields:
    if field not in data:
      errors.append(required_error(field))
      continue
    
    validator = validators[field]
    
    parsed_value = validator(field, data.get(field), errors)
    if parsed_value is not None:
      parsed[field] = parsed_value
      
  return parsed, errors
