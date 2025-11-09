from flask import Flask, jsonify, request

app = Flask(__name__)

todos = []


@app.route("/")
def home():
  return jsonify({"message": "Welcome to the To-Do API!"})

@app.route("/todos", methods=["GET"])
def get_todos():
  return jsonify(todos)

@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
  for todo in todos:
    if todo["id"] == todo_id:
      return jsonify(todo)
  return jsonify({"error": "Todo not found"}), 404

@app.route("/todos", methods=["POST"])
def create_todo():
  data = request.get_json()
  todo = {
    "id": data.get("id"),
    "title": data.get("title"),
    "completed": data.get("completed", False)
  }
  todos.append(todo)
  return jsonify(todo), 201

@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_todo(todo_id):
  data = request.get_json()
  for todo in todos:
    if todo["id"] == todo_id:
      todo.update({
        "title": data.get("title", todo["title"]),
        "completed": data.get("completed", todo["completed"])
      })
      return jsonify(todo)
  return jsonify({"error": "Todo not found"}), 404

@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
  global todos
  todos = [todo for todo in todos if todo["id"] != todo_id]
  return jsonify({"message": "Todo deleted"})

if __name__ == "__main__":
  app.run(debug=True)