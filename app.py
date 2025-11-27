from flask import Flask, jsonify, request, render_template
from models import Person, Prayer
from utils.validators import *

app = Flask(__name__)

people: list[Person] = []

# Update: may use hashmap for O(1) lookup bc binary only helps
# For VERY long lists (i.e. > 10K prayers / ppl)

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/people", methods=["GET"])
def get_people():
  relationship = parse_relationship(request.args.get("rel", None))
  
  if relationship:
    return jsonify([p.to_dict() for p in people if p.get_relationship() == relationship])
  
  return jsonify([p.to_dict() for p in people]) 

# TO DO: Change to match the URL of the submit form?
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
      person_id = people[-1].get_id() + 1 if people else 1
      person = Person(person_id, name, relationship)
      person.add_prayer_request(Prayer(prayer))
      people.append(person)
      return jsonify(person.to_dict()), 201
  
  # TO DO: Specify missing or invalid fields
  return jsonify({"error": "Missing or invalid fields"}), 400


@app.route("/people/<int:person_id>", methods=["GET"])
def get_person(person_id):
  person = next((p for p in people if p.get_id() == person_id), None)
  
  if person is None:
    return jsonify({"error": "Person not found"}), 404
  
  return jsonify(person.to_dict())

@app.route("/people/<int:person_id>", methods=["PATCH"])
def update_person(person_id):
  data = request.get_json()
  
  person = next((p for p in people if p.get_id() == person_id), None)

  if person is None:
    return jsonify({"error": "Person not found"}), 404 
    
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  
  if is_valid_string(name):
    person.set_name(name)
  
  if relationship is not None:
    person.set_relationship(relationship)
    
  return jsonify(person.to_dict())
  
@app.route("/people/<int:person_id>", methods=["DELETE"])
def delete_person(person_id):
  person = next((p for p in people if p.get_id() == person_id), None)
  
  if person is None:
    return jsonify({"error": "Person not found"}), 404
  
  people.remove(person)
  
  return '', 204


@app.route("/people/<int:person_id>/prayers", methods=["GET"])
def get_prayers(person_id):
  person = next((p for p in people if p.get_id() == person_id), None)

  if person is None:
    return jsonify({"error": "Person not found"}), 404
  
  return jsonify([prayer.to_dict() for prayer in person.get_prayer_requests()])


@app.route("/people/<int:person_id>/prayers", methods=["POST"])
def add_prayer(person_id):
  person = next((p for p in people if p.get_id() == person_id), None)

  if person is None:
    return jsonify({"error": "Person not found"}), 404
  
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", False)
  
  if is_valid_string(text) and is_valid_bool(has_prayed):
    prayer = Prayer(text, has_prayed)
    person.add_prayer_request(prayer)
    return jsonify(prayer.to_dict()), 201
  
  return jsonify({"error": "Missing or invalid fields"}), 400
  

@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["PATCH"])
def update_prayer(person_id, prayer_id):
  person = next((p for p in people if p.get_id() == person_id), None)
  
  if person is None:
    return jsonify({"error": "Person not found"}), 404 
  
  data = request.get_json()
  
  text = data.get("text", None)
  has_prayed = data.get("has_prayed", None)
  
  if not is_valid_string(text) and not is_valid_bool(has_prayed):
    return jsonify({"error": "Missing or invalid fields"}), 400
    
  for prayer in person.get_prayer_requests():
    if prayer.get_id() == prayer_id:
      
      if is_valid_string(text):
        prayer.set_text(text)
        
      if is_valid_bool(has_prayed):
        prayer.set_has_prayed(has_prayed)
        
      return jsonify(prayer.to_dict())
  
  return jsonify({"error": "Prayer not found"}), 404

@app.route("/people/<int:person_id>/prayers/<int:prayer_id>", methods=["DELETE"])
def delete_prayer(person_id, prayer_id):
  person = next((p for p in people if p.get_id() == person_id), None)

  if not person:
    return jsonify({"error": "Person not found"}), 404
  
  if not person.delete_prayer_request(prayer_id):
    return jsonify({"error": "Prayer not found"}), 404 
      
  return '', 204

if __name__ == "__main__":
  app.run(debug=True)