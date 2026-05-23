from models import Relationship
from helpers import (
  client,
  assert_success_response, 
  assert_error_response,
  assert_valid_delete_response,
  generate_person_json,
  assert_person_data, 
  update_existing_json_fields,
)

PEOPLE_URL = '/api/people'

# POST endpoint
def test_add_person_valid(client):
  people = [
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
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
  person = generate_person_json(
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
  person = generate_person_json(
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
  person = generate_person_json(
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
  person = generate_person_json(
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

def test_add_person_invalid_name(client):
  person = generate_person_json(
    name=123,
    relationship=Relationship.FRIENDS.value,
    prayer="Forgiveness"
  )

  response = client.post(PEOPLE_URL, json=person)

  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'name' must be a string."}
  )

def test_add_person_invalid_prayer(client):
  person = generate_person_json(
    name="Bob",
    relationship=Relationship.FRIENDS.value,
    prayer=123
  )

  response = client.post(PEOPLE_URL, json=person)

  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'prayer' must be a string."}
  )

def test_add_person_invalid_relationship(client):
  person = generate_person_json(
    name="Bob",
    relationship="Stranger",
    prayer="Forgiveness"
  )

  response = client.post(PEOPLE_URL, json=person)
  valid_relationships = [r.value for r in Relationship]


  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={f"'relationship' must be one of {valid_relationships}"}
  )

# GET endpoint
def test_get_people_no_filter(client):
  people = [
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
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
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
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
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")

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
  
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
  client.post(PEOPLE_URL, json=person)
    
  response = client.get(invalid_person_url)
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )
  
# PATCH endpoint
def test_update_person_valid_name_only(client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_name_json = update_existing_json_fields({"name": "Julia"}, person)
  response = client.patch(person_url, json=updated_name_json)
  
  person_data = assert_success_response(
    response, 
    expected_message="Person updated"
  )
  
  assert_person_data(person_data, person)

def test_update_person_valid_relationship_only(client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_relationship_json = update_existing_json_fields(
    {"relationship": Relationship.FRIENDS.value}, 
    person
  )
  
  response = client.patch(person_url, json=updated_relationship_json)
  
  person_data = assert_success_response(
    response, 
    expected_message="Person updated"
  )
  
  assert_person_data(person_data, person)

def test_update_person_valid_all_fields(client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_name_and_relationship_json = update_existing_json_fields(
    {"name": "Mary", "relationship": Relationship.KNOWN.value},
    person
  )
  response = client.patch(person_url, json=updated_name_and_relationship_json)

  person_data = assert_success_response(
    response, 
    expected_message="Person updated"
  )
  
  assert_person_data(person_data, person)

def test_update_person_missing_all_fields(client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  response = client.patch(person_url, json={})
  
  assert_error_response(
    response,
    expected_message="Validation failed",
    expected_errors={"'name' is required.", "'relationship' is required."}
  )
  
  get_response = client.get(person_url)
  person_data = assert_success_response(
    get_response,
    expected_message="Person retrieved"
  )
  
  assert_person_data(person_data, person)
  

# DELETE endpoint
def test_delete_person_valid(client):
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
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
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
  client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  client.delete(person_url)

  response = client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message="Person not found",
    expected_status=404
  )