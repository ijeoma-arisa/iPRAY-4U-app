def generate_person_json(name=None, relationship=None, prayer=None, person_json=None, allow_null=False):
    person_json = person_json or {}
    
    if allow_null:
        return {
            "name": name,
            "relationship": relationship,
            "prayer": prayer
        }
    
    if name is not None:
        person_json["name"] = name
    
    if relationship is not None:
        person_json["relationship"] = relationship
        
    if prayer is not None:
        person_json["prayer"] = prayer
        
    return person_json

def generate_prayer_json(prayer=None, has_prayed=False, prayer_json=None, allow_null=False):
    prayer_json = prayer_json or {}
    
    if allow_null:
        return {
            "prayer": prayer,
            "has_prayed": has_prayed
        }

    if prayer is not None:
        prayer_json["prayer"] = prayer

    if has_prayed is not None:
        prayer_json["has_prayed"] = has_prayed
        
    return prayer_json
  
def update_existing_json_fields(updated_fields: dict, json: dict):
    for field, updated_value in updated_fields.items():
        if field not in json:
            return {}
        
        json[field] = updated_value
    
    return updated_fields