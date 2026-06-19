from ipray4u.models import Relationship
from .helpers.fixtures import client, app
from .helpers.assertions import (
  assert_success_response, 
  assert_relationship_data,
)
from .helpers.urls import RELATIONSHIPS_URL
from ipray4u.utils.success_messages import get_success

def test_get_relationships(client):
  response = client.get(RELATIONSHIPS_URL)
  
  relationships_data = assert_success_response(
    response,
    expected_message=get_success("Relationships"),
    data_type=list
  )
  
  for rel in relationships_data:
    relationship_id = rel.get("id")
    assert isinstance(relationship_id, int)
    
    assert_relationship_data(relationship_id, Relationship.get_value_by_id(relationship_id))

