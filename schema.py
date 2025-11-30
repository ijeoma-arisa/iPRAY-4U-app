# TO DO: Migrate to SQLAlchemy ORM later

# TABLES
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

# INDEXES
CREATE_INDEX_ON_PEOPLE_RELATIONSHIP = """
CREATE INDEX IF NOT EXISTS idx_people_relationship ON people(relationship_id);"""

CREATE_INDEX_ON_PRAYERS_PERSON = """
CREATE INDEX IF NOT EXISTS idx_prayers_person ON prayers(person_id);"""

# SELECT QUERIES
SELECT_LAST_INSERTED_ID_QUERY = "SELECT last_insert_rowid() AS id"

# People
SELECT_ALL_PEOPLE_QUERY = "SELECT * FROM people"

SELECT_RELATIONSHIP_PEOPLE_QUERY = """
SELECT p.* 
FROM people AS p
JOIN relationships AS r ON p.relationship_id = r.id
WHERE r.relationship = ?"""

SELECT_PERSON_QUERY = "SELECT * FROM people WHERE id = ?"

# Prayers
SELECT_PRAYERS_BY_PERSON_QUERY = "SELECT * FROM prayers WHERE person_id = ?"

SELECT_PRAYER_QUERY = "SElECT * FROM prayers WHERE id = ?"

# Relationship
SELECT_RELATIONSHIP_QUERY = "SELECT id FROM RELATIONSHIPS where relationship = ?"

# INSERT QUERIES
INSERT_RELATIONSHIP_ROWS = "INSERT OR IGNORE INTO relationships (relationship) VALUES (?)"

INSERT_PERSON_QUERY = "INSERT INTO people (name, relationship_id) VALUES (?, ?)"

INSERT_DEFAULT_PRAYER_QUERY = "INSERT INTO prayers (person_id, text) VALUES (?, ?)"

INSERT_PRAYER_QUERY = "INSERT INTO prayers (person_id, text, has_prayed) VALUES (?, ?, ?)"

# UPDATE Queries
UPDATE_PERSON_NAME_QUERY = "UPDATE people SET name = ? WHERE id = ?"

UPDATE_PERSON_RELATIONSHIP_QUERY = "UPDATE people SET relationship_id = ? where id = ?"

UPDATE_PRAYER_TEXT_QUERY = "UPDATE prayers SET text = ? WHERE id = ?"

UPDATE_PRAYER_HAS_PRAYED_QUERY = "UPDATED prayers SET has_prayed = ? WHERE id = ?"