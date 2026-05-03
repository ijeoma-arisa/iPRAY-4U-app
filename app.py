import psycopg
import os
from flask import Flask, g, jsonify, request, render_template
from dotenv import load_dotenv
import db.schema_postgres as schema_postgres
from models import Relationship
from utils.validators import (
  is_valid_string,
  is_valid_bool,
  require_fields,
  parse_str,
  parse_relationship,
)

load_dotenv()

def init_db():
  with psycopg.connect(
    os.environ["DATABASE_URL"],
    row_factory=psycopg.rows.dict_row
  ) as conn:
    cursor = conn.cursor()
    
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
      
def create_app():
  app = Flask(__name__, instance_relative_config=True)
  
  with app.app_context():
    init_db()
    
  def get_db_connection():
    if "db" not in g:
      g.db = psycopg.connect(
        os.environ["DATABASE_URL"],
        row_factory=psycopg.rows.dict_row
      )
    return g.db

  @app.teardown_appcontext
  def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
      db.close()

  def rows_to_dict(rows):
    return [dict(row) for row in rows]

  def success_json(message, data={}):
    data = dict(data) if not isinstance(data, list) else rows_to_dict(data) 
    return jsonify({"status": "success", "message": message, "data": data})

  def error_json(message):
    return jsonify({"status": "error", "message": message})

  @app.route("/")
  def homepage():
    return render_template("index.html")

  @app.route("/prayer-requests")
  def prayer_requests_page():
    return render_template("prayer-requests.html")

  # TODO: Add custom 404 Not Found page (or redirect)
  @app.route("/api/people", methods=["GET"])
  def get_people():
    db = get_db_connection()
    
    relationship = parse_relationship("rel", request.args.get("rel"))
    
    people = (db.execute(schema_postgres.SELECT_RELATIONSHIP_PEOPLE_QUERY, (relationship.value,)).fetchall()
              if type(relationship) is Relationship 
              else db.execute(schema_postgres.SELECT_ALL_PEOPLE_QUERY).fetchall())
    
    return success_json("People retrieved", people)

  @app.route("/api/people", methods=["POST"])
  # TODO: Resolve duplicate people and relationships
  def add_person():
    data = request.get_json()
    
    # Check to see if any fields are missing  
    missing_fields = require_fields(data, ["name", "relationship", "prayer"])
    if missing_fields:
      return error_json(f"Missing fields: {missing_fields}"), 400
    
    # Validate fields
    name = parse_str("name", data.get("name"))
    relationship = parse_relationship("relationship", data.get("relationship"))
    prayer = parse_str("prayer", data.get("prayer"))
    
    errors = [f[0] for f in [name, relationship, prayer] if type(f) == list]
      
    #TODO: Fix formatting instead of joining with commas
    if errors:
      return error_json(f"Error: {", ".join(errors)}"), 400

    db = get_db_connection()
          
    relationship_row = db.execute(schema_postgres.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()
    
    person_id = db.execute(schema_postgres.INSERT_PERSON_QUERY, (name, relationship_row["id"])).fetchone()["id"]
    
    db.execute(schema_postgres.INSERT_DEFAULT_PRAYER_QUERY, (person_id, prayer)) 
    
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    db.commit()
    return success_json("Prayer added", person), 201
      

  @app.route("/api/people/<int:person_id>", methods=["GET"])
  def get_person(person_id):
    db = get_db_connection()
    
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404
    
    return success_json("Person retrieved", person)

  @app.route("/api/people/<int:person_id>", methods=["PATCH"])
  def update_person(person_id):
    data = request.get_json()
    
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404 
      
    name = data.get("name", None)
    relationship = parse_relationship("relationship", data.get("relationship"))
    
    # TODO: Add error message for invalid name
    if is_valid_string(name):
      db.execute(schema_postgres.UPDATE_PERSON_NAME_QUERY, (name, person_id))
    
    # TODO: Add error message for invalid relationship
    if type(relationship) is Relationship:
      relationship_id = db.execute(schema_postgres.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()["id"]
      db.execute(schema_postgres.UPDATE_PERSON_RELATIONSHIP_QUERY, (relationship_id, person_id))
      
      
    updated_person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
      
    db.commit()
    return success_json("Person updated", updated_person)
    
  @app.route("/api/people/<int:person_id>", methods=["DELETE"])
  def delete_person(person_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404
    
    db.execute(schema_postgres.DELETE_PERSON_QUERY, (person_id,))
    db.commit()
    
    return '', 204

  @app.route("/api/prayers", methods=["GET"])
  def get_prayers():
    db = get_db_connection()
    prayers = db.execute(schema_postgres.SELECT_ALL_PRAYERS_QUERY).fetchall()
    
    return success_json("Prayers retrieved", prayers)

  @app.route("/api/people/<int:person_id>/prayers", methods=["GET"])
  def get_prayers_by_person(person_id):
    db = get_db_connection()
    
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404
    
    prayers = db.execute(schema_postgres.SELECT_ALL_PRAYERS_BY_PERSON_QUERY, (person_id,)).fetchall()
    
    if prayers is None:
      return error_json("Person not found"), 404
    
    return success_json("Prayers retrieved", prayers)

  #TODO: Add more specific error message for invalid/missing fields
  @app.route("/api/people/<int:person_id>/prayers", methods=["POST"])
  def add_prayer(person_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404
    print(person_id)
    data = request.get_json()
    
    missing_fields = require_fields(data, ["prayer"])
    if missing_fields:
      return error_json(missing_fields), 400
    
    prayer = data.get("prayer")
    has_prayed = data.get("has_prayed", False)
    
    # TODO: Validate 'prayer' and 'has_prayed' data types
    # Edge case: either field is present but assigned None value
    # May update validator functions used, then delete later
    
    if is_valid_string(prayer) and is_valid_bool(has_prayed):
      prayer_id = db.execute(schema_postgres.INSERT_PRAYER_QUERY, (person_id, prayer, has_prayed)).fetchone()["id"]      
      prayer = db.execute(schema_postgres.SELECT_PRAYER_QUERY, (prayer_id,)).fetchone()
      
      db.commit()
      return success_json("Prayer added", prayer), 201
    
    return error_json("Missing or invalid fields"), 400
    

  @app.route("/api/people/<int:person_id>/prayers/<int:prayer_id>", methods=["PATCH"])
  def update_prayer(person_id, prayer_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404 
    
    prayer = db.execute(schema_postgres.SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
    
    if prayer is None:
        return error_json("Prayer not found"), 404
      
    data = request.get_json()
    
    prayer = data.get("prayer", None)
    has_prayed = data.get("has_prayed", None)
    
    if not is_valid_string(prayer) and not is_valid_bool(has_prayed):
      return error_json("Missing or invalid fields"), 400
    
    if is_valid_string(prayer):
      db.execute(schema_postgres.UPDATE_PRAYER_TEXT_QUERY, (prayer, prayer_id))
      
    if is_valid_bool(has_prayed):
      db.execute(schema_postgres.UPDATE_PRAYER_HAS_PRAYED_QUERY, (has_prayed, prayer_id))
      
    updated_prayer = db.execute(schema_postgres.SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
    
    db.commit()
    return success_json("Prayer updated", updated_prayer)
    
  #TODO: Maybe distinguish "prayer id does not exist" from that "prayer id does not belong to that person"
  @app.route("/api/people/<int:person_id>/prayers/<int:prayer_id>", methods=["DELETE"])
  def delete_prayer(person_id, prayer_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if not person:
      return error_json("Person not found"), 404 
    
    prayer = db.execute(schema_postgres.SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
    
    if not prayer:
      return error_json("Prayer not found"), 404 
    
    db.execute(schema_postgres.DELETE_PRAYER_QUERY, (prayer_id,))
    db.commit() 
        
    return '', 204

  @app.route("/api/relationships", methods=["GET"])
  def get_relationships():
      db = get_db_connection()
      relationships = db.execute(schema_postgres.SELECT_ALL_RELATIONSHIPS_QUERY).fetchall()
          
      return success_json("Relationships retrieved", relationships)
  
  return app

app = create_app()

if __name__ == "__main__":
  app.run(debug=True)