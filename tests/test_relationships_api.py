from models import Relationship
from helpers import (
  client,
  assert_success_response, 
  assert_relationship_data,
)

RELATIONSHIP_URL = '/api/relationships'

def test_get_relationships(client):
  response = client.get(RELATIONSHIP_URL)
  
  relationships_data = assert_success_response(
    response,
    expected_message="Relationships retrieved",
    data_type=list
  )
  
  for rel in relationships_data:
    relationship_id = rel.get("id")
    assert isinstance(relationship_id, int)
    
    assert_relationship_data(relationship_id, Relationship.get_value_by_id(relationship_id))

