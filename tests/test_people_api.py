from models import Relationship
from helpers import (
  client,
  assert_success_response, 
  assert_error_response,
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
  
  data = assert_success_response(
    response, 
    expected_message="People retrieved",
    data_type=list
  )

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
    
    data = assert_success_response(
      response, 
      expected_message="People retrieved",
      data_type=list
    )
    
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
    
    data = assert_success_response(
      response, 
      expected_message="Person added",
      expected_status=201
    )
        
    assert isinstance(data.get("id"), int)
    assert data.get("name") == person["name"]
    
    relationship_id = data.get("relationship_id")
    assert isinstance(relationship_id, int)
    
    relationship_list = list(Relationship) 
    assert 0 <= relationship_id - 1 < len(relationship_list)
    assert relationship_list[relationship_id - 1].value == person["relationship"]
  
def test_add_person_missing_name(client):
  person = generate_sample_person(
    name=None, 
    relationship=Relationship.FRIENDS.value, 
    prayer="Forgiveness"
  )

  people_url = get_people_url()
  response = client.post(people_url, json=person)
  
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'name' is required."}
  )
  
def test_add_person_missing_relationship(client):
  person = generate_sample_person(
    name="Bob", 
    relationship=None, 
    prayer="Forgiveness"
  )

  people_url = get_people_url()
  response = client.post(people_url, json=person)
  
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'relationship' is required."}
  )
  
def test_add_person_missing_prayer(client):
  person = generate_sample_person(
    name="Bob", 
    relationship=Relationship.FRIENDS.value, 
    prayer=None
  )

  people_url = get_people_url()
  response = client.post(people_url, json=person)
  
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'prayer' is required."}
  )

def test_add_person_missing_all_fields(client):
  person = generate_sample_person(
    name=None,
    relationship=None,
    prayer=None
  )
  
  people_url = get_people_url()
  response = client.post(people_url, json=person)
  
  required_fields = ["name", "relationship", "prayer"]
  required_field_errors = set(f"'{field}' is required." for field in required_fields)
    
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors=required_field_errors
  )

