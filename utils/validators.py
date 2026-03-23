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
    
def validate_str(field, value):
  if not isinstance(value, str):
    return f"{field} must be a string. Received type {type(value)}"
  if value.strip() == "":
    return f"{field} must be a non-empty string"
  
  
def parse_relationship(relationship_str: str) -> Relationship:
  if not is_valid_string(relationship_str):
    return "Not a valid string"
  
  relationship_str = relationship_str.strip().title()
  
  for relationship_type in Relationship:
    if relationship_type.value == relationship_str:
      return relationship_type
  return "Selected relationship does not exist"