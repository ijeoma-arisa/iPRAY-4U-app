from flask import Blueprint, render_template, request, flash
from . import success_json, error_json
from ipray4u.supabase_client import get_supabase

auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.get("/signup")
def signup_page():
    return render_template("signup.html")

@auth_blueprint.post("/signup")
def post_signup():   
    supabase = get_supabase()
     
    email = request.form.get("email")
    password =  request.form.get("password")
    
    # supabase.auth.sign_up(
    #     {
    #     "email": email,
    #     "password": password,
    #     }
    # )
    
    # flash('Account created', 'success') 
        