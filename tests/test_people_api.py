from models import Relationship
from helpers import (
  client,
  assert_success_response, 
  assert_errors_response,
  generate_sample_person, 
)

def get_people_url(relationship = None) -> str:
  people_url = '/api/people'
  
  if relationship is None:
    return people_url 
  
  return f"{people_url }?rel={relationship.lower()}"
    
def test_get_people_no_filter(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
  
  people_url = get_people_url()
  
  for person in people:
    client.post(people_url, json=person)
 
  response = client.get(people_url)
  
  data = assert_success_response(response, data_type=list)

  assert isinstance(data, list)
  assert len(data) == 3
  
def test_get_people_with_relationship_filter(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
  
  people_url = get_people_url()
  
  for person in people:
    client.post(people_url, json=person)
    
    response = client.get(get_people_url(person["relationship"]))    
    
    data = assert_success_response(response, data_type=list)
    
    assert isinstance(data, list)
    assert len(data) == 1
    
  
def test_add_person_valid(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
  
  people_url = get_people_url()
  
  for person in people:
    response = client.post(people_url, json=person)
    
    data = assert_success_response(response, expected_status=201)
    
    assert isinstance(data, dict)
    assert "id" in data
    assert "name" in data
    assert "relationship_id" in data
  
    
# def test_add_person_missing_name(client):
#   person_json = {
#     "relationship": "Friends",
#     "prayer": "To pass my exam"
#   }
  
#   response = client.post(PEOPLE_URL, json=person_json)

#   assert response.status_code == 400
#   assert response.is_json
  
  