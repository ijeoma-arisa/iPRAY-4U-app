from models import Relationship

def parse_bool_default(value, default_bool: bool = False) -> bool:
  return value if isinstance(value, bool) else default_bool

def parse_str(field, value, errors) -> str | None:
  if not isinstance(value, str):
    errors.append(f"'{field}' must be a string.")
    return None
  
  value = value.strip()
  
  if value == "":
    errors.append(f"'{field}' must be a non-empty string.")
    return None
  
  return value
  
def parse_relationship(field, value, errors) -> Relationship | None:
  if not isinstance(value, str):
    errors.append(f"'{field}' must be a string.")
    return None
  
  relationship_str = value.strip().lower()
  
  for relationship_type in Relationship:
    if relationship_type.value.lower() == relationship_str:
      return relationship_type
  
  valid_relationships = [r.value for r in Relationship]
  errors.append(f"'{field}' must be one of {valid_relationships}")
  
  return None


validators = {
  "name": parse_str,
  "relationship": parse_relationship,
  "prayer": parse_str
}

def validate_fields(data, required_fields=None) -> tuple[list, dict]:
  required_fields = required_fields or []
  errors = []
  parsed = {}
  
  for field in required_fields:
    if field not in data:
      errors.append(f"'{field}' is required.")
      continue
    
    validator = validators[field]
    parsed[field] = validator(field, data.get(field), errors)
      
  return parsed, errors
