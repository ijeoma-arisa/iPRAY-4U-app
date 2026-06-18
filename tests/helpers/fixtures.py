import pytest
import os
from types import SimpleNamespace

from ipray4u import create_app
from ipray4u.db import get_db_connection, cleanup_test_db
from dotenv import load_dotenv

from ipray4u.models import Relationship 
from .urls import PEOPLE_URL, get_prayers_url
from .sample_data import generate_person_json
from .assertions import assert_success_response
from ipray4u.utils.success_messages import get_success, post_success

load_dotenv()

@pytest.fixture
def app():
  app = create_app({
    "TESTING": True,
    "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
    "WTF_CSRF_ENABLED": False,
  })
  
  cleanup_test_db()

  yield app
  
  cleanup_test_db()


@pytest.fixture
def client(app):
  return app.test_client()

@pytest.fixture
def test_user(app):
  user = {
    "id": "00000000-0000-0000-0000-000000000001",
    "email": "test@example.com",
    "display_name": "Test User",
  }
  
  with app.app_context():
    db = get_db_connection()
  
    db.execute(
      """
      INSERT INTO auth.users (id)
      VALUES (%s)
      ON CONFLICT (id) DO NOTHING
      """,
      (user["id"],)
    )
    
    db.execute(
      """
      INSERT INTO profiles (id, display_name)
      VALUES (%s, %s)
      ON CONFLICT (id) DO NOTHING
      """
      (user["id"], user["display_name"])
    )
    
    db.commit()
    db.close()
  
 
  return user
  
  
@pytest.fixture
def auth_client(client, test_user):
  with client.session_transaction() as session:
    session["user_id"] = test_user["id"] 
    session["email"] = test_user["email"]
    
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

@pytest.fixture
def auth_form_data():
  return {
    "email": "test@example.com",
    "password": "test-password",
  }
  
@pytest.fixture
def mock_supabase(mocker):
  fake_supabase = mocker.Mock()
  
  mocker.patch(
    "ipray4u.routes.auth.get_supabase",
    return_value=fake_supabase
  )
  
  return fake_supabase

@pytest.fixture
def mock_login_response():
    return SimpleNamespace(
        user=SimpleNamespace(
            id="00000000-0000-0000-0000-000000000001",
            email="test@example.com",
        )
  )  
  