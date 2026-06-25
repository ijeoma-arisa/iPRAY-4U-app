from flask import (
    Blueprint, 
    render_template,
    make_response,
)

from ipray4u.decorators import login_required

pages_blueprint = Blueprint("pages", __name__)

@pages_blueprint.get("/")
def homepage():
    response = make_response(render_template("index.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@pages_blueprint.get("/prayer-requests")
@login_required
def prayer_requests_page():
    response = make_response(render_template("prayer-requests.html"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response