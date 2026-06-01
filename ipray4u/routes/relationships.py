from flask import Blueprint

from . import success_json
from ipray4u.db import get_db_connection, schema
from ipray4u.utils.success_messages import get_success

relationships_blueprint = Blueprint("relationships", __name__)

@relationships_blueprint.route("/api/relationships", methods=["GET"])
def get_relationships():
    db = get_db_connection()
    relationships = db.execute(schema.SELECT_ALL_RELATIONSHIPS_QUERY).fetchall()
        
    return success_json(get_success("Relationships"), relationships)
  