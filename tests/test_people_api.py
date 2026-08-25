from ipray4u.models import Relationship
from ipray4u.db import get_db_connection

from .helpers.assertions import (
    assert_success_response, 
    assert_error_response,
    assert_valid_delete_response,
    assert_person_data, 
)
from .helpers.sample_data import generate_person_json, update_existing_json_fields
from .helpers.urls import PEOPLE_URL

from ipray4u.utils.error_messages import (
  DUPLICATE_PERSON_ERROR,
  VALIDATION_FAILED_ERROR,
  AUTHENTICATION_REQUIRED_ERROR,
  required_error,
  string_error,
  valid_relationship_error,
  not_found_error,
)

from ipray4u.utils.success_messages import (
  get_success,
  post_success,
  patch_success,
)

# POST endpoint
def test_add_person_requires_auth(client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  
  response = client.post(PEOPLE_URL, json=person)
  
  assert_error_response(
    response,
    expected_message=AUTHENTICATION_REQUIRED_ERROR,
    expected_status=401
  )

def test_add_person_valid(auth_client):
  people = [
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
  ]
    
  for person in people:
    response = auth_client.post(PEOPLE_URL, json=person)
    
    person_data = assert_success_response(
      response, 
      expected_message=post_success("Person"),
      expected_status=201
    )
    
    assert_person_data(person_data, person)

def test_add_person_rejects_duplicate_normalized_name(auth_client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  response = auth_client.post(PEOPLE_URL, json=person)

  assert_success_response(
    response,
    expected_message=post_success("Person"),
    expected_status=201,
  )

  for duplicate_name in ["Bob", "  bOB  "]:
    duplicate = generate_person_json(
      duplicate_name,
      Relationship.FAMILY.value,
      "Peace"
    )
    response = auth_client.post(PEOPLE_URL, json=duplicate)

    assert_error_response(
      response,
      expected_message=DUPLICATE_PERSON_ERROR,
      expected_status=409,
    )

def test_add_person_allows_same_name_for_different_users(auth_client, app):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  response = auth_client.post(PEOPLE_URL, json=person)

  assert_success_response(
    response,
    expected_message=post_success("Person"),
    expected_status=201,
  )

  second_user_id = "00000000-0000-0000-0000-000000000002"
  with app.app_context():
    db = get_db_connection()
    db.execute("INSERT INTO auth.users (id) VALUES (%s)", (second_user_id,))
    db.execute(
      "INSERT INTO profiles (id, display_name) VALUES (%s, %s)",
      (second_user_id, "Second User")
    )
    db.commit()

  with auth_client.session_transaction() as session:
    session["user_id"] = second_user_id

  response = auth_client.post(PEOPLE_URL, json=person)

  assert_success_response(
    response,
    expected_message=post_success("Person"),
    expected_status=201,
  )
   
def test_add_person_missing_name(auth_client):
  person = generate_person_json(
    name=None, 
    relationship=Relationship.FRIENDS.value, 
    prayer="Forgiveness"
  )

  response = auth_client.post(PEOPLE_URL, json=person)
  
  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={required_error("name")}
  )
  
def test_add_person_missing_relationship(auth_client):
  person = generate_person_json(
    name="Bob", 
    relationship=None, 
    prayer="Forgiveness"
  )

  response = auth_client.post(PEOPLE_URL, json=person)
  
  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={required_error("relationship")}
  )
  
def test_add_person_missing_prayer(auth_client):
  person = generate_person_json(
    name="Bob", 
    relationship=Relationship.FRIENDS.value, 
    prayer=None
  )

  response = auth_client.post(PEOPLE_URL, json=person)
  
  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={required_error("prayer")}
  )

def test_add_person_missing_all_fields(auth_client):
  person = generate_person_json(
    name=None,
    relationship=None,
    prayer=None
  )
  
  response = auth_client.post(PEOPLE_URL, json=person)
  
  required_field_errors = required_error(["name", "relationship", "prayer"])
    
  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors=set(required_field_errors),
  )

def test_add_person_invalid_name(auth_client):
  person = generate_person_json(
    name=123,
    relationship=Relationship.FRIENDS.value,
    prayer="Forgiveness"
  )

  response = auth_client.post(PEOPLE_URL, json=person)

  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={string_error("name")}
  )

def test_add_person_invalid_prayer(auth_client):
  person = generate_person_json(
    name="Bob",
    relationship=Relationship.FRIENDS.value,
    prayer=123
  )

  response = auth_client.post(PEOPLE_URL, json=person)

  assert_error_response(
    response,
   expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={string_error("prayer")}
  )

def test_add_person_invablid_relationship(auth_client):
  person = generate_person_json(
    name="Bob",
    relationship="Stranger",
    prayer="Forgiveness"
  )

  response = auth_client.post(PEOPLE_URL, json=person)

  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors={valid_relationship_error("relationship")}
  )

# GET endpoint
def test_get_people_requires_auth(client):
  response = client.get(PEOPLE_URL)
  
  assert_error_response(
    response,
    expected_message=AUTHENTICATION_REQUIRED_ERROR,
    expected_status=401
  )
  
def test_get_people_no_filter(auth_client):
  people = [
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
  ]
    
  for person in people:
    auth_client.post(PEOPLE_URL, json=person)
 
  response = auth_client.get(PEOPLE_URL)
  
  data = assert_success_response(
    response, 
    expected_message=get_success("People"),
    data_type=list
  )

  assert isinstance(data, list)
  assert len(data) == 3

  for person_data, person in zip(data, people):
    assert_person_data(person_data, person)
  
def test_get_people_with_relationship_filter(auth_client):
  people = [
    generate_person_json("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_person_json("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_person_json("Chris", Relationship.KNOWN.value, "Peace"),
  ]

  for person in people:
    auth_client.post(PEOPLE_URL, json=person)
    
    relationship_url = f"{PEOPLE_URL}?rel={person["relationship"]}"
    response = auth_client.get(relationship_url)    
    
    data = assert_success_response(
      response, 
      expected_message=get_success("People"),
      data_type=list
    )
    
    assert isinstance(data, list)
    assert len(data) == 1
    assert_person_data(data[0], person)
    
def test_get_person_valid(auth_client):
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")

  auth_client.post(PEOPLE_URL, json=person)
    
  person_url = f"{PEOPLE_URL}/1"
  response = auth_client.get(person_url) 
  
  person_data = assert_success_response(
    response, 
    expected_message=get_success("Person"),
  )
  
  assert_person_data(person_data, person)
  
def test_get_person_invalid(auth_client):
  invalid_person_url = f"{PEOPLE_URL}/2"
  response = auth_client.get(invalid_person_url)
  
  assert_error_response(
    response,
    expected_message=not_found_error("Person"),
    expected_status=404
  )
  
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
  auth_client.post(PEOPLE_URL, json=person)
    
  response = auth_client.get(invalid_person_url)
  assert_error_response(
    response,
    expected_message=not_found_error("Person"),
    expected_status=404
  )
  
# PATCH endpoint
def test_update_person_requires_auth(client, sample_person):
  person_id = sample_person["id"]
  person_url = f"{PEOPLE_URL}/{person_id}"
  
  with client.session_transaction() as session:
    session.clear()
  
  updated_name_json = {"name": "Sarah"}
  update_existing_json_fields(updated_name_json, sample_person)
  response = client.patch(person_url, json=updated_name_json)
    
  assert_error_response(
    response,
    expected_message=AUTHENTICATION_REQUIRED_ERROR,
    expected_status=401
  )
  
def test_update_person_valid_name_only(auth_client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_name_json = update_existing_json_fields({"name": "Julia"}, person)
  response = auth_client.patch(person_url, json=updated_name_json)
  
  person_data = assert_success_response(
    response, 
    expected_message=patch_success("Person"),
  )
  
  assert_person_data(person_data, person)

def test_update_person_valid_relationship_only(auth_client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_relationship_json = update_existing_json_fields(
    {"relationship": Relationship.FRIENDS.value}, 
    person
  )
  
  response = auth_client.patch(person_url, json=updated_relationship_json)
  
  person_data = assert_success_response(
    response, 
    expected_message=patch_success("Person"),
  )
  
  assert_person_data(person_data, person)

def test_update_person_valid_all_fields(auth_client):
  person = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  updated_name_and_relationship_json = update_existing_json_fields(
    {"name": "Mary", "relationship": Relationship.KNOWN.value},
    person
  )
  response = auth_client.patch(person_url, json=updated_name_and_relationship_json)

  person_data = assert_success_response(
    response, 
    expected_message=patch_success("Person"),
  )
  
  assert_person_data(person_data, person)

def test_update_person_rejects_duplicate_normalized_name(auth_client):
  bob = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  sarah = generate_person_json("Sarah", Relationship.FAMILY.value, "Peace")

  for person in [bob, sarah]:
    response = auth_client.post(PEOPLE_URL, json=person)
    assert_success_response(
      response,
      expected_message=post_success("Person"),
      expected_status=201,
    )

  response = auth_client.patch(f"{PEOPLE_URL}/2", json={"name": "  bOB  "})

  assert_error_response(
    response,
    expected_message=DUPLICATE_PERSON_ERROR,
    expected_status=409,
  )

  unchanged_person = assert_success_response(
    auth_client.get(f"{PEOPLE_URL}/2"),
    expected_message=get_success("Person"),
  )
  assert unchanged_person["name"] == "Sarah"

def test_update_person_missing_all_fields(auth_client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  
  response = auth_client.patch(person_url, json={})
  
  assert_error_response(
    response,
    expected_message=VALIDATION_FAILED_ERROR,
    expected_errors=set(required_error(["name", "relationship"]))
  )
  
  get_response = auth_client.get(person_url)
  person_data = assert_success_response(
    get_response,
    expected_message=get_success("Person")
  )
  
  assert_person_data(person_data, person)
  

# DELETE endpoint
def test_delete_person_requires_auth(client, sample_person):
  person_id = sample_person["id"]
  person_url = f"{PEOPLE_URL}/{person_id}"
  
  with client.session_transaction() as session:
    session.clear()
  
  response = client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message=AUTHENTICATION_REQUIRED_ERROR,
    expected_status=401
  )
  
def test_delete_person_valid(auth_client):
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  response = auth_client.delete(person_url)

  assert_valid_delete_response(response)
  
def test_delete_person_nonexistent_id(auth_client):
  person_url = f"{PEOPLE_URL}/1"
  response = auth_client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message=not_found_error("Person"),
    expected_status=404
  )
  
def test_delete_person_duplicate_request(auth_client):
  person = generate_person_json("Sam", Relationship.FAMILY.value, "Obedience")
  auth_client.post(PEOPLE_URL, json=person)
  
  person_url = f"{PEOPLE_URL}/1"
  auth_client.delete(person_url)

  response = auth_client.delete(person_url)
  
  assert_error_response(
    response,
    expected_message=not_found_error("Person"),
    expected_status=404
  )
