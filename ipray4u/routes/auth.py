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
from ipray4u.db.profiles import ensure_profile_exists

MIN_PASSWORD_LENGTH = 8

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
     
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm-password", "")
    
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "error")
        return render_template("signup.html", email=email), 400
    
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("signup.html", email=email), 400
    
    supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )
    
    flash("Account created. Check your email to verify your account.", "info")
    
    return redirect(url_for("auth.verify_page"))
        
@auth_blueprint.get("/login")
def login_page():
    return render_template("login.html")

@auth_blueprint.post("/login")
def login_user():
    supabase = get_supabase()
    
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": request.form.get("email"),
                "password": request.form.get("password"),
            }
        )
        
        user_id = response.user.id
        email = response.user.email
        
        ensure_profile_exists(user_id)
        
        session["user_id"] = user_id
        session["email"] = email
        
        flash("Welcome back!", "success")
        return redirect(url_for("pages.prayer_requests_page"))
        
    except AuthApiError:
        flash("Invalid email or password.", "error")
        return redirect(url_for("auth.login_page"))
    
    except Exception:
        current_app.logger.exception("Unexpected error during login")
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login_page"))

@auth_blueprint.post("/logout")
def logout_user():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login_page"))
    