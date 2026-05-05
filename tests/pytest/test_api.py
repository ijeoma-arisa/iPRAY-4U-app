import pytest
import os
from dotenv import load_dotenv
from app import create_app
from db import cleanup_test_db
from tests.sample_data_helpers import generate_sample_person
from models import Relationship

PEOPLE_URL = '/api/people'

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
  
  
def assert_success_response(response, expected_status=200):
  assert response.status_code == expected_status
  assert response.is_json
  
  json = response.get_json()
  assert "data" in json
  
  return json["data"]
  
  
def test_get_people(client):
  people = [
    generate_sample_person("Bob", Relationship.FRIENDS.value, "Strength"),
    generate_sample_person("Sarah",  Relationship.FAMILY.value, "Peace"),
    generate_sample_person("Chris", Relationship.KNOWN.value, "Peace"),
  ]
  
  for person in people:
    client.post(PEOPLE_URL, json=person)
 
  response = client.get(PEOPLE_URL)
  
  data = assert_success_response(response)

  assert isinstance(data, list)
  assert len(data) == 3
  
def test_add_person_valid(client):
  person_json = {
    "name": "Billy",
    "relationship": "Friends",
    "prayer": "To pass my exam"
  }
  
  response = client.post(PEOPLE_URL, json=person_json)
  
  assert response.status_code == 201
    
def test_add_person_missing_name(client):
  person_json = {
    "relationship": "Friends",
    "prayer": "To pass my exam"
  }
  
  response = client.post(PEOPLE_URL, json=person_json)

  assert response.status_code == 400
  assert response.is_json
  
  