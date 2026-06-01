from flask import Blueprint
from . import success_json, error_json

auth_blueprint = Blueprint("auth", __name__)