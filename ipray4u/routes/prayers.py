from flask import Blueprint, request

from ipray4u.responses import success_json, error_json
from ipray4u.db import get_db_connection, schema
from ipray4u.utils.validators import validate_fields, parse_bool_default
from ipray4u.utils.error_messages import VALIDATION_FAILED_ERROR, not_found_error
from ipray4u.utils.success_messages import (
    get_success,
    post_success,
    patch_success,
)
from ipray4u.decorators import api_login_required

prayers_blueprint = Blueprint("prayers", __name__)

@prayers_blueprint.get("/api/prayers")
@api_login_required
def get_prayers():
    db = get_db_connection()
    prayers = db.execute(schema.SELECT_ALL_PRAYERS_QUERY).fetchall()
    
    return success_json(get_success("Prayers"), prayers)

@prayers_blueprint.get("/api/people/<int:person_id>/prayers")
@api_login_required
def get_prayers_by_person(person_id):
    db = get_db_connection()
    
    person = db.execute(schema.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json(not_found_error("Person")), 404
    
    prayers = db.execute(schema.SELECT_ALL_PRAYERS_BY_PERSON_QUERY, (person_id,)).fetchall()
    
    success_msg = "No prayers found" if not prayers else get_success("Prayers")
    
    return success_json(success_msg, prayers)

@prayers_blueprint.post("/api/people/<int:person_id>/prayers")
@api_login_required
def add_prayer(person_id):
    db = get_db_connection()
    person = db.execute(schema.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if person is None:
      return error_json(not_found_error("Person")), 404
    
    data = request.get_json()
    
    required_fields = ["prayer"]
    parsed, errors = validate_fields(data, required_fields)
    
    if errors:
      return error_json(VALIDATION_FAILED_ERROR, errors), 400
    
    prayer_text = parsed["prayer"]
    has_prayed = parse_bool_default(data.get("has_prayed"))
    
    prayer = db.execute(schema.INSERT_PRAYER_QUERY, (person_id, prayer_text, has_prayed)).fetchone()   
      
    db.commit()
    return success_json(post_success("Prayer"), prayer), 201
        
@prayers_blueprint.patch("/api/people/<int:person_id>/prayers/<int:prayer_id>")
@api_login_required
def update_prayer(person_id, prayer_id):
    data = request.get_json()
    
    valid_fields = ["prayer", "has_prayed"]
    parsed, errors = validate_fields(data, valid_fields)
    
    prayer = parsed.get("prayer")
    has_prayed = parsed.get("has_prayed")
    
    if not parsed or (prayer is None and has_prayed is None):
      return error_json(VALIDATION_FAILED_ERROR, errors), 400
    
    
    db = get_db_connection()

    if prayer is not None and has_prayed is not None:
      updated_prayer = db.execute(schema.UPDATE_PRAYER_TEXT_AND_HAS_PRAYED_QUERY, (prayer, has_prayed, prayer_id)).fetchone()
    elif prayer is not None:
      updated_prayer = db.execute(schema.UPDATE_PRAYER_TEXT_QUERY, (prayer, prayer_id)).fetchone()
    else:
      updated_prayer = db.execute(schema.UPDATE_PRAYER_HAS_PRAYED_QUERY, (has_prayed, prayer_id)).fetchone()
 
    if updated_prayer is None:
        return error_json(not_found_error("Prayer")), 404
      
    db.commit()
    return success_json(patch_success("Prayer"), updated_prayer)
    
@prayers_blueprint.delete("/api/people/<int:person_id>/prayers/<int:prayer_id>")
@api_login_required
def delete_prayer(person_id, prayer_id):
    db = get_db_connection()
    person = db.execute(schema.SELECT_PERSON_QUERY, (person_id,)).fetchone()
    
    if not person:
      return error_json(not_found_error("Person")), 404 
    
    deleted_prayer = db.execute(schema.DELETE_PRAYER_QUERY, (prayer_id,)).fetchone()
    
    if deleted_prayer is None:
      return error_json(not_found_error("Prayer")), 404 
    
    db.commit() 
        
    return '', 204