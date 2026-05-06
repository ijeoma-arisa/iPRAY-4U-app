import pytest
import os
from dotenv import load_dotenv
from app import create_app
from db import cleanup_test_db
from helpers.sample_data import generate_sample_person
from models import Relationship


def get_people_url(relationship = None) -> str:
  people_url = '/api/people'
  
  if relationship is None:
    return people_url 
  
  return f"{people_url }?rel={relationship.lower()}"
    

load_dotenv()

@pytest.fixture
def client():
  app = create_app({
    "DATABASE_URL": os.environ["TEST_DATABASE_URL"]
  })
    
  client = app.test_client()
  
  cleanup_test_db()

  yield client
  
  cleanup_test_db()


def assert_success_response(response, data_type=dict, expected_status=200):
  assert response.status_code == expected_status
  assert response.is_json
  
  json = response.get_json()
  
  assert "status" in json
  assert json["status"] == "success"
  
  assert "message" in json
  assert isinstance(json["message"], str)
  assert len(json["message"]) > 0
  
  assert "data" in json
  assert isinstance(json["data"], data_type)
  assert len(json["data"]) > 0

  
  return json["data"]
  
def assert_errors_response(response, expected_status=400):
  assert response.status_code == expected_status
  assert response.is_json
  
  json = response.get_json()
  
  assert "status" in json
  assert isinstance(json["message"], str)
  assert len(json["message"]) > 0
    
  assert "message" in json
  assert isinstance(json["message"], str)
  assert len(json["message"]) > 0
  
  if "errors" in json:
    errors = json["errors"]
    assert isinstance(errors, list)
    assert len(errors) > 0
    
  return json
  
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
  
  