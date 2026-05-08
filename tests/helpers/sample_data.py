def generate_person_json(name=None, relationship=None, prayer=None, person_json=None):
      person_json = person_json or {}
      
      if name is not None:
          person_json["name"] = name
      
      if relationship is not None:
          person_json["relationship"] = relationship
          
      if prayer is not None:
          person_json["prayer"] = prayer
          
      return person_json
  
def update_existing_json_fields(updated_fields: dict, json: dict):
    for field, updated_value in updated_fields.items():
        if field not in json:
            return {}
        
        json[field] = updated_value
    
    return updated_fields