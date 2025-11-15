from flask import Flask, jsonify, request, render_template
from models import Person, Prayer
from utils.validators import is_valid_string, parse_relationship

app = Flask(__name__)

persons: list[Person] = []

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/prayer-requests", methods=["GET"])
def get_prayer_requests_all():
  return jsonify([person.to_dict() for person in persons]) 

@app.route("/prayer-requests/<relationship>", methods=["GET"])
def get_prayer_requests_relationship(relationship):
  result = []
  for person in persons:
    if person.get_relationship().value.lower() == relationship.lower():
      result.append(person.to_dict())
  return jsonify(result)

@app.route("/prayer-requests/<int:person_id>", methods=["GET"])
def get_person(person_id):
  for person in persons:
    if person.get_id() == person_id:
      return jsonify(person.to_dict())
  return jsonify({"error": "Person not found"}), 404

@app.route("/prayer-requests", methods=["POST"])
def create_prayer_request():
  data = request.get_json()
  
  person_id = data.get("id", None)
  name = data.get("name", None)
  relationship = parse_relationship(data.get("relationship", None))
  
  if person_id and name and relationship:
    person = Person(person_id, name, relationship)
    persons.append(person)
    return jsonify(person.to_dict()), 201
  
  # TO DO: Specify missing or invalid fields
  return jsonify({"error": "Missing or invalid fields"}), 400
    
  
  # person = None
  # if person_id is not None:
  #   for person in persons:
  #     if person.get_id() == person_id:
  #       person = person
  #       break
  # person = person if person else 
    
  # if person_id is not None:
  #   prayer_request = {
  #     "id": data.get("id"),
  #     "person": data.get("person"),
  #     "text": data.get("text"),
  #     "prayed": data.get("prayed", False)
  #   }
  #   prayer_requests.append(prayer_request)
  #   return jsonify(prayer_request), 201
    

# @app.route("/prayer-requests/<int:prayer_request_id>", methods=["PUT"])
# def update_prayer_request(prayer_request_id):
#   data = request.get_json()
#   for prayer_request in prayer_requests:
#     if prayer_request["id"] == prayer_request_id:
#       prayer_requests.update({
#         "person": data.get("person", prayer_request["person"]),
#         "text": data.get("text", prayer_request["text"]),
#         "prayed": data.get("prayed", prayer_request["prayed"])
#       })
#       return jsonify(prayer_request)
#   return jsonify({"error": "Prayer request not found"}), 404

# @app.route("/prayer-requests/<int:prayer_request_id>", methods=["DELETE"])
# def delete_prayer_request(prayer_request_id):
#   global prayer_requests
#   prayer_requests = [prayer_request for prayer_request in prayer_requests if prayer_request["id"] != prayer_request_id]
#   return jsonify({"message": "Prayer request deleted"})

if __name__ == "__main__":
  app.run(debug=True)