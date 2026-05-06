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
  