import pytest
import os
from app import create_app
from db import cleanup_test_db
from dotenv import load_dotenv

from models import Relationship 
from helpers.urls import PEOPLE_URL, get_prayers_url
from helpers.sample_data import generate_person_json
from helpers.assertions import assert_success_response
from utils.success_messages import get_success, post_success

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

@pytest.fixture
def sample_person(client):
  person = generate_person_json("Bob", Relationship.FRIENDS.value, "Strength")
  response = client.post(PEOPLE_URL, json=person)
  
  data = assert_success_response(
    response,
    expected_message=post_success("Person"),
    expected_status=201    
  )
  
  return data

@pytest.fixture
def sample_prayer(client, sample_person):
  person_id = sample_person["id"]
  prayers_url = get_prayers_url(person_id)
  
  response = client.get(prayers_url)
  
  
  prayers = assert_success_response(
    response,
    expected_message=get_success("Prayers"),
    data_type=list
  )
  
  assert isinstance(prayers, list)
  assert len(prayers) == 1
  
  return prayers[0]