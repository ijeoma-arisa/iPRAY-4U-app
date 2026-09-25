from datetime import datetime

from flask import jsonify

def _serialize_value(value):
    if isinstance(value, datetime):
      return value.isoformat()
    return value

def _row_to_dict(row):
    return {key: _serialize_value(value) for key, value in dict(row).items()}

def _rows_to_dict(rows):
    return [_row_to_dict(row) for row in rows]

def success_json(message, data=None):
    if data is None:
      data = {}
    
    data = _row_to_dict(data) if not isinstance(data, list) else _rows_to_dict(data)
    
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
