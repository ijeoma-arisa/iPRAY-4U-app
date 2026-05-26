import pytest
import os
from app import create_app
from db import cleanup_test_db
from dotenv import load_dotenv

from models import Relationship 
from helpers.urls import PEOPLE_URL
from helpers.sample_data import generate_person_json
from helpers.assertions import assert_success_response
from utils.success_messages import post_success

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