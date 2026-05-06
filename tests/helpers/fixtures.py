import pytest
import os
from app import create_app
from db import cleanup_test_db
from dotenv import load_dotenv

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
