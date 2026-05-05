import pytest
from app import create_app, init_db

PEOPLE_URL = '/api/people'

@pytest.fixture
def client():
  app = create_app({
    "DATABASE_URL": "test_db_url"
  })
  
  yield client
  
  return app.test_client()

def test_get_person(client):
  response = client.get(PEOPLE_URL)
  
  assert response.status_code == 200
  assert response.is_json
  
  data = response.get_json()
  assert isinstance(data, list)
  

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
  
  