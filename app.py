import os
from flask import Flask, g, jsonify, request, render_template
from dotenv import load_dotenv

from db import init_db, get_db_connection, schema_postgres
from models import Relationship
from utils.validators import (
  validate_fields,
  parse_relationship,
  parse_bool_default
)

load_dotenv()

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  
  app.config["DATABASE_URL"] = os.environ["PROD_DATABASE_URL"]
  
  if test_config:
    app.config.update(test_config)
  
  with app.app_context():
    init_db()
    
  @app.teardown_appcontext
  def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
      db.close()

  def rows_to_dict(rows):
    return [dict(row) for row in rows]

  def success_json(message, data=None):
    if data is None:
      data = {}
    
    data = dict(data) if not isinstance(data, list) else rows_to_dict(data) 
    
    return jsonify({
      "status": "success", 
      "message": message, 
      "data": data
    })

  def error_json(message, errors=None):
    body = {
      "status": "error",
      "message": message
    }
    
    if errors is not None:
      body["errors"] = errors
      
    return jsonify(body)

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
    
    relationship = parse_relationship("rel", request.args.get("rel"), [])
    
    people = (db.execute(schema_postgres.SELECT_RELATIONSHIP_PEOPLE_QUERY, (relationship.value,)).fetchall()
              if isinstance(relationship, Relationship)
              else db.execute(schema_postgres.SELECT_ALL_PEOPLE_QUERY).fetchall())
    
    return success_json("People retrieved", people)

  @app.route("/api/people", methods=["POST"])
  # TODO: Resolve duplicate people and relationships
  def add_person():
    data = request.get_json()
    
    required_fields = ["name", "relationship", "prayer"]
    parsed, errors = validate_fields(data, required_fields)
    
    if errors:
      return error_json("Validation failed", errors), 400
    
    name = parsed["name"]
    relationship = parsed["relationship"]
    prayer = parsed["prayer"]
   
    db = get_db_connection()

    relationship_row = db.execute(schema_postgres.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()   
    person_id = db.execute(schema_postgres.INSERT_PERSON_QUERY, (name, relationship_row["id"])).fetchone()["id"]
    
    db.execute(schema_postgres.INSERT_DEFAULT_PRAYER_QUERY, (person_id, prayer)) 
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    db.commit()
    return success_json("Person added", person), 201
      

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
    
    required_fields = ["name", "relationship"]
    parsed, errors = validate_fields(data, required_fields)
    
    if errors:
      return error_json("Validation failed", errors), 400
    
    name = parsed["name"]
    relationship = parsed["relationship"]
     
    db = get_db_connection()
    
    relationship_id = db.execute(schema_postgres.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()["id"]
    updated_person = db.execute(schema_postgres.UPDATE_PERSON_QUERY, (name, relationship_id, person_id)).fetchone()
    
    if updated_person is None:
      return error_json("Person not found"), 404
    
    db.commit()
    return success_json("Person updated", updated_person)
    
  @app.route("/api/people/<int:person_id>", methods=["DELETE"])
  def delete_person(person_id):
    db = get_db_connection()
    
    deleted_person = db.execute(schema_postgres.DELETE_PERSON_QUERY, (person_id,)).fetchone()
    
    if deleted_person is None:
      return error_json("Person not found"), 404
    
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
    
    success_msg = "No prayers found" if not prayers else "Prayers retrieved"
    
    return success_json(success_msg, prayers)

  @app.route("/api/people/<int:person_id>/prayers", methods=["POST"])
  def add_prayer(person_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404
    
    data = request.get_json()
    
    required_fields = ["prayer"]
    parsed, errors = validate_fields(data, required_fields)
    
    if errors:
      return error_json("Validation failed", errors), 400
    
    prayer_text = parsed["prayer"]
    has_prayed = parse_bool_default(data.get("has_prayed"))
    
    prayer = db.execute(schema_postgres.INSERT_PRAYER_QUERY, (person_id, prayer_text, has_prayed)).fetchone()   
      
    db.commit()
    return success_json("Prayer added", prayer), 201
        

  @app.route("/api/people/<int:person_id>/prayers/<int:prayer_id>", methods=["PATCH"])
  def update_prayer(person_id, prayer_id):
    data = request.get_json()
    
    required_fields = ["prayer"]
    parsed, errors = validate_fields(data, required_fields)
    
    if errors:
      return error_json("Validation failed", errors), 400
    
    prayer_text = parsed["prayer"]
    has_prayed = parse_bool_default(data.get("has_prayed"))
    
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json("Person not found"), 404 
    
    updated_prayer = db.execute(schema_postgres.UPDATE_PRAYER_QUERY, (prayer_text, has_prayed, prayer_id)).fetchone()
  
    if updated_prayer is None:
        return error_json("Prayer not found"), 404
      
    db.commit()
    return success_json("Prayer updated", updated_prayer)
    
  @app.route("/api/people/<int:person_id>/prayers/<int:prayer_id>", methods=["DELETE"])
  def delete_prayer(person_id, prayer_id):
    db = get_db_connection()
    person = db.execute(schema_postgres.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if not person:
      return error_json("Person not found"), 404 
    
    deleted_prayer = db.execute(schema_postgres.DELETE_PRAYER_QUERY, (prayer_id,)).fetchone()
    
    if deleted_prayer is None:
      return error_json("Prayer not found"), 404 
    
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