# TO DO: Migrate to SQLAlchemy ORM later

# Tables
CREATE_RELATIONSHIPS_TABLE = """
CREATE TABLE IF NOT EXISTS relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  relationship TEXT NOT NULL UNIQUE
  );"""

CREATE_PEOPLE_TABLE = """
CREATE TABLE IF NOT EXISTS people (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  relationship_id INTEGER NOT NULL,
  CONSTRAINT fk_relationship FOREIGN KEY (relationship_id) REFERENCES relationships (id)
  );"""
  
CREATE_PRAYERS_TABLE = """
CREATE TABLE IF NOT EXISTS prayers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  person_id INTEGER NOT NULL,
  text TEXT NOT NULL,
  has_prayed INTEGER NOT NULL DEFAULT 0 CHECK (has_prayed IN (0,1)),
  CONSTRAINT fk_person FOREIGN KEY (person_id) REFERENCES people (id) ON DELETE CASCADE
  );"""

# Indexes
CREATE_INDEX_ON_PEOPLE_RELATIONSHIP = """
CREATE INDEX IF NOT EXISTS idx_people_relationship ON people(relationship_id);"""

CREATE_INDEX_ON_PRAYERS_PERSON = """
CREATE INDEX IF NOT EXISTS idx_prayers_person ON prayers(person_id);"""

# Select Queries
SELECT_ALL_PEOPLE_QUERY = "SELECT * FROM people"

SELECT_PERSON_QUERY = "SELECT * FROM people WHERE id = ?"

SELECT_PRAYERS_BY_PERSON_QUERY = "SELECT * FROM prayers WHERE person_id = ?"

# SELECT_RELATIONSHIP_QUERY = "SELECT * FROM people WHERE "