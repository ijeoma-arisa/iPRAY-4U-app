from flask import jsonify

def _rows_to_dict(rows):
    return [dict(row) for row in rows]

def success_json(message, data=None):
    if data is None:
      data = {}
    
    data = dict(data) if not isinstance(data, list) else _rows_to_dict(data) 
    
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