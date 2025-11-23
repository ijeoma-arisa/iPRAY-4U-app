from flask import Flask, jsonify, request, render_template
from models import Person, Prayer
from utils.validators import is_valid_string, is_valid_int, parse_relationship

app = Flask(__name__)

persons: list[Person] = []

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/persons", methods=["GET"])
def get_persons():
  return jsonify([person.to_dict() for person in persons]) 

# TO DO: Change to match the URL of the submit form?
@app.route("/persons", methods=["POST"])
def add_person():
  data = request.get_json()
  
  person_id = data.get("id", None)
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  prayer = data.get("prayer", None)
  
    
  if (is_valid_int(person_id) and 
    is_valid_string(name) and 
    relationship is not None and 
    is_valid_string(prayer)
    ):
      person = Person(person_id, name, relationship)
      person.add_prayer_request(Prayer(prayer))
      persons.append(person)
      return jsonify(person.to_dict()), 201
  
  # TO DO: Specify missing or invalid fields
  return jsonify({"error": "Missing or invalid fields"}), 400
      
@app.route("/persons/<relationship>", methods=["GET"])
def get_persons_relationship(relationship):
  result = []
  
  relationship = parse_relationship(relationship)
  
  if relationship is None:
    return jsonify({"error": "Missing or invalid relationship value"}), 404 
  
  for person in persons:
    if person.get_relationship() == relationship:
      result.append(person.to_dict())
  return jsonify(result)

@app.route("/persons/<int:person_id>", methods=["GET"])
def get_person(person_id):
  for person in persons:
    if person.get_id() == person_id:
      return jsonify(person.to_dict())
  return jsonify({"error": "Person not found"}), 404

@app.route("/persons/<int:person_id>", methods=["PATCH"])
def update_person(person_id):
  data = request.get_json()
  
  person_to_update = None
  for person in persons:
    if person.get_id() == person_id:
      person_to_update = person
      break
  
  if not person_to_update:
    return jsonify({"error": "Person not found"}), 404 
    
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  
  if is_valid_string(name):
    person.set_name(name)
  
  if relationship:
    person.set_relationship(relationship)
    
  return jsonify(person.to_dict())
  
@app.route("/persons/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
    
  person_to_delete = None
  for person in persons:
    if person.get_id() == person_id:
      person_to_delete = person
      break
  
  if not person_to_delete:
    return jsonify({"error": "Person not found"}), 404
  
  persons.remove(person_to_delete)

  return jsonify({"message": "Person deleted"})

# TO DO: ADD ID FOR PRAYERS IF NEEDED 
@app.route("/persons/<int:person_id>/prayers", methods=["GET"])
def get_prayers(person_id):
  pass

@app.route("/persons/<int:person_id>/prayers", methods=["POST"])
def add_prayer(person_id):
  pass

@app.route("/persons/<int:person_id>/prayers", methods=["PATCH"])
def update_prayer(person_id):
  pass

@app.route("/persons/<int:person_id>/prayers", methods=["DELETE"])
def delete_prayer(person_id):
  pass

if __name__ == "__main__":
  app.run(debug=True)