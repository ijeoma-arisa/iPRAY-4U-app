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
