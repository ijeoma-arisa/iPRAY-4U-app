from flask import Flask, jsonify, request, render_template
from models import Person, Prayer

app = Flask(__name__)

persons: list[Person] = []

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/prayer-requests/all", methods=["GET"])
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

# TO DO: FINISH THE REST
# @app.route("/prayer-requests", methods=["POST"])
# def create_prayer_request():
#   data = request.get_json()
#   person_id = data.get("id", None)
  
#   if person_id is not None:
#     for person in persons:
#       if person.get_id() == person_id:
#         break
#   person = person if person else 
    
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