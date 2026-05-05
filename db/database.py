import os
import psycopg
from flask import g, current_app
from db import schema_postgres
from models import Relationship
from dotenv import load_dotenv

load_dotenv()

def init_db():
  with psycopg.connect(
    current_app.config["DATABASE_URL"],
    row_factory=psycopg.rows.dict_row
  ) as conn:
    
    with conn.cursor() as cursor:
      # Create tables
      cursor.execute(schema_postgres.CREATE_RELATIONSHIPS_TABLE)
      cursor.execute(schema_postgres.CREATE_PEOPLE_TABLE)
      cursor.execute(schema_postgres.CREATE_PRAYERS_TABLE)
      
      # Create indexes
      cursor.execute(schema_postgres.CREATE_INDEX_ON_PEOPLE_RELATIONSHIP)
      cursor.execute(schema_postgres.CREATE_INDEX_ON_PRAYERS_PERSON)
      
      # Insert relationship values
      relationship_values = [(r.value,) for r in Relationship]
      cursor.executemany(schema_postgres.INSERT_RELATIONSHIP_ROWS, relationship_values)
    
def get_db_connection():
  if "db" not in g:
    g.db = psycopg.connect(
      current_app.config["DATABASE_URL"],
      row_factory=psycopg.rows.dict_row
    )
  return g.db
 
def cleanup_test_db():
  with psycopg.connect(
    os.environ["TEST_DATABASE_URL"]
  ) as conn:
    
    with conn.cursor() as cursor:
      cursor.execute("""
        TRUNCATE TABLE prayers, people
        RESTART IDENTITY CASCADE;
        """)