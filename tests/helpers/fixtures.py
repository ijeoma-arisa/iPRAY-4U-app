import pytest
import os
from ipray4u import create_app
from ipray4u.db import cleanup_test_db
from dotenv import load_dotenv

from ipray4u.models import Relationship 
from .urls import PEOPLE_URL, get_prayers_url
from .sample_data import generate_person_json
from .assertions import assert_success_response
from ipray4u.utils.success_messages import get_success, post_success

load_dotenv()

@pytest.fixture
def client():
  app = create_app({
    "TESTING": True,
    "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
    "WTF_CSRF_ENABLED": False,
  })

  client = app.test_client()
  
  cleanup_test_db()

  yield client
  
  cleanup_test_db()

@pytest.fixture
def auth_client(client):
  with client.session_transaction() as session:
    session["user_id"] = "test-user-id"
    session["email"] = "test@example.com"
    
  return client

@pytest.fixture
def sample_person(auth_client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  response = auth_client.post(PEOPLE_URL, json=person)
  
  data = assert_success_response(
    response,
    expected_message=post_success("Person"),
    expected_status=201    
  )
  
  return data

@pytest.fixture
def sample_prayer(auth_client, sample_person):
  person_id = sample_person["id"]
  prayers_url = get_prayers_url(person_id)
  
  response = auth_client.get(prayers_url)
  
  prayers = assert_success_response(
    response,
    expected_message=get_success("Prayers"),
    data_type=list
  )
  
  assert isinstance(prayers, list)
  assert len(prayers) == 1
  
  return prayers[0]