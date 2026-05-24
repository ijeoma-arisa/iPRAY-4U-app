from models import Relationship

def assert_valid_delete_response(response):
  assert response.status_code == 204
  assert len(response.text) == 0

def assert_success_response(response, expected_message, data_type=dict, expected_status=200):
  assert response.status_code == expected_status
  assert response.is_json
  
  json = response.get_json()
  
  assert json.get("status") == "success"
  
  message = json.get("message")
  assert message == expected_message
  
  data = json.get("data")
  assert isinstance(data, data_type)

  return data
  
def assert_error_response(response, expected_message, expected_errors=None, expected_status=400):
  assert response.status_code == expected_status
  assert response.is_json
  
  json = response.get_json()
  
  assert json.get("status") == "error"
  
  message = json.get("message")
  assert message == expected_message
  
  if expected_errors is not None:
    errors = json.get("errors")
    assert isinstance(errors, list)
    assert set(errors) == expected_errors
    
  return json

 
def assert_relationship_data(relationship_id, expected_relationship):
  assert Relationship.get_value_by_id(relationship_id).lower() == expected_relationship.lower()
  
def assert_person_data(data: dict, person: dict):
  assert isinstance(data.get("id"), int)
  assert data.get("name") == person["name"]
  
  relationship_id = data.get("relationship_id")
  assert isinstance(relationship_id, int)
  
  assert_relationship_data(relationship_id, person["relationship"])

def assert_prayer_data(data: dict, prayer: dict):
  assert isinstance(data.get("id"), int)
  assert data.get("prayer") == prayer["prayer"]
  assert data.get("has_prayed") == prayer["has_prayed"]
  
  person_id = data.get("person_id")
  assert isinstance(person_id, int)
  
