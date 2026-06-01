from flask import Blueprint, render_template

pages_blueprint = Blueprint("pages", __name__)
@pages_blueprint.get("/")
def homepage():
    return render_template("index.html")

@pages_blueprint.get("/prayer-requests")
def prayer_requests_page():
    return render_template("prayer-requests.html")
