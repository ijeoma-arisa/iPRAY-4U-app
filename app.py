from flask import Flask, jsonify, request, render_template
from models import Person, Prayer
from utils.validators import *

app = Flask(__name__)

people: list[Person] = []

# TO DO: Use binary search to find id in array -> O(logn) instead of O(n)

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/people", methods=["GET"])
def get_people():
  return jsonify([person.to_dict() for person in people]) 

# TO DO: Change to match the URL of the submit form?
@app.route("/people", methods=["POST"])
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
      people.append(person)
      return jsonify(person.to_dict()), 201
  
  # TO DO: Specify missing or invalid fields
  return jsonify({"error": "Missing or invalid fields"}), 400
      
@app.route("/people/<relationship>", methods=["GET"])
def get_people_relationship(relationship):
  result = []
  
  relationship = parse_relationship(relationship)
  
  if relationship is None:
    return jsonify({"error": "Missing or invalid relationship value"}), 404 
  
  for person in people:
    if person.get_relationship() == relationship:
      result.append(person.to_dict())
  return jsonify(result)

@app.route("/people/<int:person_id>", methods=["GET"])
def get_person(person_id):
  for person in people:
    if person.get_id() == person_id:
      return jsonify(person.to_dict())
  return jsonify({"error": "Person not found"}), 404

@app.route("/people/<int:person_id>", methods=["PATCH"])
def update_person(person_id):
  data = request.get_json()
  
  person_to_update = None
  for person in people:
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
  
@app.route("/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
  person_to_delete = None
  for person in people:
    if person.get_id() == person_id:
      person_to_delete = person
      break
  
  if not person_to_delete:
    return jsonify({"error": "Person not found"}), 404
  
  people.remove(person_to_delete)

  return jsonify({"message": "Person deleted"})


@app.route("/people/<int:person_id>/prayers", methods=["GET"])
def get_prayers(person_id):
  person_to_view = None
  for person in people:
    if person.get_id() == person_id:
      person_to_view = person
      break
  
  if person_to_view is None:
    return jsonify({"error": "Person not found"}), 404
  
  return jsonify([prayer.to_dict() for prayer in person_to_view.get_prayer_requests()])

  

@app.route("/people/<int:person_id>/prayers", methods=["POST"])
def add_prayer(person_id):
  person_to_update = None
  for person in people:
    if person.get_id() == person_id:
        person_to_update = person
        break
      
  if person_to_update is None:
    return jsonify({"error": "Person not found"}), 404
  
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", False)
  
  if is_valid_string(text) and is_valid_bool(has_prayed):
    prayer = Prayer(text, has_prayed)
    person_to_update.add_prayer_request(prayer)
    return jsonify(prayer.to_dict())
  
  return jsonify({"error": "Missing or invalid fields"}), 400
  

@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["PATCH"])
def update_prayer(person_id, prayer_id):
  person_to_update = None
  for person in people:
    if person.get_id() == person_id:
      person_to_update = person
      break
  
  if not person_to_update:
    return jsonify({"error": "Person not found"}), 404 
  
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", None)
  
  if not is_valid_string(text) and not is_valid_bool(has_prayed):
    return jsonify({"error": "Missing or invalid fields"})
    
  for prayer in person_to_update.get_prayer_requests():
    if prayer.get_id() == prayer_id:
      
      if is_valid_string(text):
        prayer.set_text(text)
        
      if is_valid_bool(has_prayed):
        prayer.set_has_prayed(has_prayed)
        
      return jsonify(prayer.to_dict())
  
  return jsonify({"error": "Prayer not found"})
      
      
      
      
      
      
  
  
  

@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["DELETE"])
def delete_prayer(person_id, prayer_id):
  pass

if __name__ == "__main__":
  app.run(debug=True)