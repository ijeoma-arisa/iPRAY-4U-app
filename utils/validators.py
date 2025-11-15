from models import Relationship

def is_valid_string(value) -> bool:
  return isinstance(value, str) and value.strip() != ""


def is_valid_int(value) -> int:
  return isinstance(value, int) and value > 0


def require_str(value, field_name):
  if not is_valid_string(value):
    raise ValueError(f"{field_name} must be a non-empty string.")
  
  
def require_fields(data, fields):
  missing = [f for f in fields if data.get(f) is None]
  
  if missing:
    raise ValueError(f"Missing required fields: {','.join(missing)}")
  
  
def parse_relationship(relationship_str: str) -> Relationship | None:
  if not is_valid_string(relationship_str):
    return None
  
  relationship_str = relationship_str.strip().title()
  
  for relationship_type in Relationship:
    if relationship_type.value == relationship_str:
      return relationship_type
  return None