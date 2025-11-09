from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

prayer_requests = []

@app.route("/")
def home():
  return render_template("index.html")

@app.route("/prayer-requests", methods=["GET"])
def get_prayer_requests():
  return jsonify(prayer_requests)

@app.route("/prayer_request/<int:prayer_request_id>", methods=["GET"])
def get_prayer_request(prayer_request_id):
  for prayer_request in prayer_requests:
    if prayer_request["id"] == prayer_request_id:
      return jsonify(prayer_request)
  return jsonify({"error": "Prayer request not found"}), 404

@app.route("/prayer-requests", methods=["POST"])
def create_prayer_request():
  data = request.get_json()
  prayer_request = {
    "id": data.get("id"),
    "person": data.get("person"),
    "text": data.get("text"),
    "prayed": data.get("prayed", False)
  }
  prayer_requests.append(prayer_request)
  return jsonify(prayer_request), 201

@app.route("/prayer_request/<int:prayer_request_id>", methods=["PUT"])
def update_prayer_request(prayer_request_id):
  data = request.get_json()
  for prayer_request in prayer_requests:
    if prayer_request["id"] == prayer_request_id:
      prayer_requests.update({
        "person": data.get("person", prayer_request["person"]),
        "text": data.get("text", prayer_request["text"]),
        "prayed": data.get("prayed", prayer_request["prayed"])
      })
      return jsonify(prayer_request)
  return jsonify({"error": "Prayer request not found"}), 404

@app.route("/prayer_request/<int:prayer_request_id>", methods=["DELETE"])
def delete_prayer_request(prayer_request_id):
  global prayer_requests
  prayer_requests = [prayer_request for prayer_request in prayer_requests if prayer_request["id"] != prayer_request_id]
  return jsonify({"message": "Prayer request deleted"})

if __name__ == "__main__":
  app.run(debug=True)