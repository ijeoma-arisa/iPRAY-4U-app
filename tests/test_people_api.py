from models import Relationship
from helpers import (
  client,
  assert_success_response, 
  assert_error_response,
  assert_valid_delete_response,
  generate_sample_person,
  assert_person_data, 
)

PEOPLE_URL = '/api/people'

# POST endpoint
def test_add_person_valid(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
    
  for person in people:
    response = client.post(PEOPLE_URL, json=person)
    
    person_data = assert_success_response(
      response, 
      expected_message="Person added",
      expected_status=201
    )
    
    assert_person_data(person_data, person)
   
def test_add_person_missing_name(client):
  person = generate_sample_person(
    name=None, 
    relationship=Relationship.FRIENDS.value, 
    prayer="Forgiveness"
  )

  response = client.post(PEOPLE_URL, json=person)
  
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

  response = client.post(PEOPLE_URL, json=person)
  
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

  response = client.post(PEOPLE_URL, json=person)
  
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
  
  response = client.post(PEOPLE_URL, json=person)
  
  required_fields = ["name", "relationship", "prayer"]
  required_field_errors = set(f"'{field}' is required." for field in required_fields)
    
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors=required_field_errors
  )

# GET endpoint

def test_get_people_no_filter(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
    
  for person in people:
    client.post(PEOPLE_URL, json=person)
 
  response = client.get(PEOPLE_URL)
  
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

  
  for person in people:
    client.post(PEOPLE_URL, json=person)
    
    relationship_url = f"{PEOPLE_URL}?rel={person["relationship"]}"
    response = client.get(relationship_url)    
    
    data = assert_success_response(
      response, 
      expected_message="People retrieved",
      data_type=list
    )
    
    assert isinstance(data, list)
    assert len(data) == 1
    
def test_get_person_valid(client):
  person = generate_sample_person("Sam", Relationship.FAMILY.value, "Obedience")

  client.post(PEOPLE_URL, json=person)
    
  person_url = f"{PEOPLE_URL}/1"
  response = client.get(person_url) 
  
  person_data = assert_success_response(
    response, 
    expected_message="Person retrieved",
  )
  
  assert_person_data(person_data, person)
  
def test_get_person_invalid(client):
  invalid_person_url = f"{PEOPLE_URL}/2"
  response = client.get(invalid_person_url)
  
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )
  
  person = generate_sample_person("Sam", Relationship.FAMILY.value, "Obedience")
  client.post(PEOPLE_URL, json=person)
    
  response = client.get(invalid_person_url)
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )
  
# PATCH endpoint
# TODO: Revisit PATCH requests - fix branching logic
def test_update_person_valid_name_only(client):
  person = generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  response = client.patch(person_url, json={"name": "Julia"})
  person["name"] = "Julia"
  
  print(response.text)
  person_data = assert_success_response(
    response, 
    expected_message="Person updated"
  )
  
  assert_person_data(person_data, person)

# def test_update_person_valid_relationship_only(client):
#   pass

# def test_update_person_valid_all_fields(client):
#   pass

# def test_update_person_invalid_(client):
#   pass

# DELETE endpoint
def test_delete_person_valid(client):
  person = generate_sample_person("Sam", Relationship.FAMILY.value, "Obedience")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  response = client.delete(person_url)

  assert_valid_delete_response(response)
  
def test_delete_person_nonexistent_id(client):
  person_url = f"{PEOPLE_URL}/1"
  response = client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )
  
def test_delete_person_duplicate_request(client):
  person = generate_sample_person("Sam", Relationship.FAMILY.value, "Obedience")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  client.delete(person_url)

  response = client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )