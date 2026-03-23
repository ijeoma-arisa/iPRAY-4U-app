from models import Relationship

def is_valid_string(value) -> bool:
  return isinstance(value, str) and value.strip() != ""

def is_valid_int(value) -> bool:
  return isinstance(value, int) and value > 0

def is_valid_int_as_bool(value) -> bool:
  return isinstance(value, int) and (value == 0 or value == 1)

def require_str(value, field_name):
  if not is_valid_string(value):
    raise ValueError(f"{field_name} must be a non-empty string.")
  
  
def require_fields(data, fields):
  missing = [f for f in fields if data.get(f) is None]
  
  return missing
  #if missing:
    # raise ValueError(f"Missing required fields: {','.join(missing)}")
    

def parse_str(field, value):
  if value is None:
    return ["error", f"Missing field '{field}'"]
  if not isinstance(value, str):
    return ["error", f"'{field}' must be a string. Received type {type(value)}."]
  if value.strip() == "":
    return ["error", f"'{field}' must be a non-empty string."]
  
  return value
  
def parse_relationship(field, value) -> Relationship:
  relationship_str = parse_str(field, value)
  if type(relationship_str) != str:
    return relationship_str
    
  relationship = relationship_str.strip().title()
  
  for relationship_type in Relationship:
    if relationship_type.value == relationship:
      return relationship_type
    
  return ["error", f"Relationship '{relationship_str}' does not exist."]