from flask import Blueprint, request

from . import success_json, error_json
from ipray4u.db import get_db_connection, schema
from ipray4u.models import Relationship
from ipray4u.utils.validators import validate_fields, parse_relationship
from ipray4u.utils.error_messages import VALIDATION_FAILED_ERROR, not_found_error
from ipray4u.utils.success_messages import (
    get_success,
    post_success,
    patch_success,
)

people_blueprint = Blueprint("people", __name__)

# TODO: Add custom 404 Not Found page (or redirect)
@people_blueprint.get("/api/people")
def get_people():
        db = get_db_connection()

        relationship = parse_relationship("rel", request.args.get("rel"), [])

        people = (db.execute(schema.SELECT_RELATIONSHIP_PEOPLE_QUERY, (relationship.value,)).fetchall()
                    if isinstance(relationship, Relationship)
                    else db.execute(schema.SELECT_ALL_PEOPLE_QUERY).fetchall())

        return success_json(get_success("People"), people)

@people_blueprint.post("/api/people")
# TODO: Resolve duplicate people and relationships
def add_person():
    data = request.get_json()

    required_fields = ["name", "relationship", "prayer"]
    parsed, errors = validate_fields(data, required_fields)

    if errors:
        return error_json(VALIDATION_FAILED_ERROR, errors), 400

    name = parsed["name"]
    relationship = parsed["relationship"]
    prayer = parsed["prayer"]

    db = get_db_connection()

    relationship_row = db.execute(schema.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()   
    person_id = db.execute(schema.INSERT_PERSON_QUERY, (name, relationship_row["id"])).fetchone()["id"]

    db.execute(schema.INSERT_DEFAULT_PRAYER_QUERY, (person_id, prayer)) 
    person = db.execute(schema.SELECT_PERSON_QUERY, (person_id,)).fetchone()

    db.commit()
    return success_json(post_success("Person"), person), 201
        

@people_blueprint.get("/api/people/<int:person_id>")
def get_person(person_id):
    db = get_db_connection()

    person = db.execute(schema.SELECT_PERSON_QUERY, (person_id,)).fetchone()

    if person is None:
        return error_json(not_found_error("Person")), 404

    return success_json(get_success("Person"), person)

@people_blueprint.patch("/api/people/<int:person_id>")
def update_person(person_id):
    data = request.get_json()

    valid_fields = ["name", "relationship"]
    parsed, errors = validate_fields(data, valid_fields)

    name = parsed.get("name")
    relationship = parsed.get("relationship")

    if not parsed or (name is None and relationship is None):
        return error_json(VALIDATION_FAILED_ERROR, errors), 400

    db = get_db_connection()

    relationship_id = db.execute(schema.SELECT_RELATIONSHIP_QUERY, (relationship.value,)).fetchone()["id"] if relationship is not None else None

    if name is not None and relationship is not None:
        updated_person = db.execute(schema.UPDATE_PERSON_NAME_AND_RELATIONSHIP_QUERY, (name, relationship_id, person_id)).fetchone()
    elif name is not None:
        updated_person = db.execute(schema.UPDATE_PERSON_NAME_QUERY, (name, person_id)).fetchone()
    else:
        updated_person = db.execute(schema.UPDATE_PERSON_RELATIONSHIP_QUERY, (relationship_id, person_id)).fetchone()

    if updated_person is None:
        return error_json(not_found_error("Person")), 404

    db.commit()
    return success_json(patch_success("Person"), updated_person)

@people_blueprint.delete("/api/people/<int:person_id>")
def delete_person(person_id):
    db = get_db_connection()

    deleted_person = db.execute(schema.DELETE_PERSON_QUERY, (person_id,)).fetchone()

    if deleted_person is None:
        return error_json(not_found_error("Person")), 404

    db.commit()

    return '', 204