from flask import Flask, g, jsonify, request, render_template
from utils.validators import *
from schema import *
import sqlite3

app = Flask(__name__)

DB_PATH = "./instance/prayer_requests.db"

def init_db():
  
  with sqlite3.connect(DB_PATH) as conn:
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute(CREATE_RELATIONSHIPS_TABLE)
    cursor.execute(CREATE_PEOPLE_TABLE)
    cursor.execute(CREATE_PRAYERS_TABLE)
    
    # Create indexes
    cursor.execute(CREATE_INDEX_ON_PEOPLE_RELATIONSHIP)
    cursor.execute(CREATE_INDEX_ON_PRAYERS_PERSON)
    
    # Insert relationship values
    relationship_values = [(r.value,) for r in Relationship]
    cursor.executemany(INSERT_RELATIONSHIP_ROWS, relationship_values)

def get_db_connection():
  if "db" not in g:
    g.db = sqlite3.connect(DB_PATH)
    g.db.row_factory = sqlite3.Row
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
  print(data)
  return jsonify({"status": "success", "message": message, "data": data})

def error_json(message):
  return jsonify({"status": "error", "message": message})

@app.route("/")
def homepage():
  return render_template("index.html")

@app.route("/prayer-requests")
def prayer_requests_page():
  return render_template("prayer-requests.html")

@app.route("/people", methods=["GET"])
def get_people():
  db = get_db_connection()
  
  relationship = parse_relationship(request.args.get("rel", None))
  
  people = (db.execute(SELECT_RELATIONSHIP_PEOPLE_QUERY, (relationship.value,)).fetchall()
            if relationship 
            else db.execute(SELECT_ALL_PEOPLE_QUERY).fetchall())
  
  return success_json("People retrieved", people)

@app.route("/people", methods=["POST"])
def add_person():
  data = request.get_json()
  
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  prayer = data.get("prayer", None)
  
  if (is_valid_string(name) and 
      relationship is not None 
      and is_valid_string(prayer)
      ):
    
      db = get_db_connection()
            
      relationship_row = db.execute(SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()
      db.execute(INSERT_PERSON_QUERY, (name, relationship_row["id"]))
      
      person_id = db.execute(SELECT_LAST_INSERTED_ID_QUERY).fetchone()["id"]      
      db.execute(INSERT_DEFAULT_PRAYER_QUERY, (person_id, prayer)) 
      db.commit()
      
      person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
      return success_json("Prayer added", person), 201
  
  return error_json("Missing or invalid fields"), 400

@app.route("/people/<int:person_id>", methods=["GET"])
def get_person(person_id):
  db = get_db_connection()
  
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  if person is None:
    return error_json("Person not found"), 404
  
  return success_json("Person retrieved", person)

@app.route("/people/<int:person_id>", methods=["PATCH"])
def update_person(person_id):
  data = request.get_json()
  
  db = get_db_connection()
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  
  if person is None:
    return error_json("Person not found"), 404 
    
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  
  if is_valid_string(name):
    db.execute(UPDATE_PERSON_NAME_QUERY, (name, person_id))
  
  if relationship is not None:
    relationship_id = db.execute(SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()["id"]
    db.execute(UPDATE_PERSON_RELATIONSHIP_QUERY, (relationship_id, person_id))
    
  db.commit()
    
  updated_person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
  return success_json("Person updated", updated_person)
  
@app.route("/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
  db = get_db_connection()
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  
  if person is None:
    return error_json("Person not found"), 404
  
  db.execute(DELETE_PERSON_QUERY, (person_id,))
  db.commit()
  
  return success_json("Person deleted"), 204


@app.route("/people/<int:person_id>/prayers", methods=["GET"])
def get_prayers(person_id):
  db = get_db_connection()
  prayers = db.execute(SELECT_ALL_PRAYERS_BY_PERSON_QUERY, (person_id,)).fetchall()
  
  if prayers is None:
    return error_json("Person not found"), 404
  
  return success_json("Prayers retrieved", prayers)


@app.route("/people/<int:person_id>/prayers", methods=["POST"])
def add_prayer(person_id):
  db = get_db_connection()
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  
  if person is None:
    return error_json("Person not found"), 404
  
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", False)
  
  if is_valid_string(text) and is_valid_int_as_bool(has_prayed):
    db.execute(INSERT_PRAYER_QUERY, (person_id, text, has_prayed))
    db.commit()
    
    prayer_id = db.execute(SELECT_LAST_INSERTED_ID_QUERY).fetchone()["id"]
    prayer = db.execute(SELECT_PRAYER_QUERY, (prayer_id,)).fetchone()
    
    return success_json("Prayer added", prayer), 201
  
  return error_json("Missing or invalid fields"), 400
  

@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["PATCH"])
def update_prayer(person_id, prayer_id):
  db = get_db_connection()
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  
  if person is None:
    return error_json("Person not found"), 404 
  
  prayer = db.execute(SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
  
  if prayer is None:
      return error_json("Prayer not found"), 404
    
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", None)
  
  if not is_valid_string(text) and not is_valid_int_as_bool(has_prayed):
    return error_json("Missing or invalid fields"), 400
  
  if is_valid_string(text):
    db.execute(UPDATE_PRAYER_TEXT_QUERY, (text, prayer_id))
    
  if is_valid_int_as_bool(has_prayed):
    db.execute(UPDATE_PRAYER_HAS_PRAYED_QUERY, (has_prayed, prayer_id))
    
  db.commit()
  
  updated_prayer = db.execute(SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
  return success_json("Prayer updated", updated_prayer)
  
@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["DELETE"])
def delete_prayer(person_id, prayer_id):
  db = get_db_connection()
  person = db.execute(SELECT_PERSON_QUERY, (person_id,)).fetchone()
  
  if not person:
    return error_json("Person not found"), 404 
  
  prayer = db.execute(SELECT_PRAYER_BY_PERSON_QUERY, (prayer_id, person_id)).fetchone()
  
  if not prayer:
    return error_json("Prayer not found"), 404 
  
  db.execute(DELETE_PRAYER_QUERY, (prayer_id,))
  db.commit() 
      
  return '', 204

@app.route("/relationships", methods=["GET"])
def get_relationships():
    db = get_db_connection()
    relationships = db.execute(SELECT_ALL_RELATIONSHIPS_QUERY).fetchall()
        
    return success_json("Relationships retrieved", relationships)
    

if __name__ == "__main__":
  init_db()
  app.run(debug=True)