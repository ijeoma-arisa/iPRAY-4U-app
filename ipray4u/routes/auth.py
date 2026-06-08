from flask import (
    Blueprint, 
    render_template, 
    request, 
    flash,
    redirect,
    url_for,
    current_app,
    session,
)
from supabase_auth.errors import AuthApiError
from ipray4u.supabase_client import get_supabase


auth_blueprint = Blueprint("auth", __name__)

@auth_blueprint.get("/verify")
def verify_page():
    return render_template("verify.html")

@auth_blueprint.get("/signup")
def signup_page():
    return render_template("signup.html")

@auth_blueprint.post("/signup")
def signup_user():   
    supabase = get_supabase()
     
    email = request.form.get("email")
    password =  request.form.get("password")
    
    # supabase.auth.sign_up(
    #     {
    #     "email": email,
    #     "password": password,
    #     }
    # )
    
    flash(
        'Account created. Check your email to verify your account.', 
        'success'
    )
    
    return redirect(url_for("auth.verify_page"))
        
@auth_blueprint.get("/login")
def login_page():
    return render_template("login.html")

@auth_blueprint.post("/login")
def login_user():
    supabase = get_supabase()
    
    email = request.form.get("email")
    password = request.form.get("password")
    
    try:
        # TODO: Remove mock login after Supabase Auth rate limit clears
        
        # response = supabase.auth.sign_in_with_password(
        #     {
        #         "email": email,
        #         "password": password,
        #     }
        # )
        
        # session["user_id"] = response.user.id
        # session["email"] = response.user.email
        
        session["user_id"] = "00000000-0000-0000-0000-000000000001"
        session["email"] = "test@example.com"
        
        flash("Welcome back!")
        return redirect(url_for("pages.prayer_requests_page"))
        
    except AuthApiError:
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login_page"))
    
    except Exception:
        current_app.logger.exception("Unexpected error during login")
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login_page"))
        
    