from models import Relationship

def is_valid_string(value) -> bool:
  return isinstance(value, str) and value.strip() != ""

def parse_relationship(relationship_str: str) -> Relationship | None:
  if not is_valid_string(relationship_str):
    return None
  
  relationship_str = relationship_str.strip().title()
  
  for relationship_type in Relationship:
    if relationship_type.value == relationship_str:
      return relationship_type
  return None