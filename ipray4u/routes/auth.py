import hashlib
import re

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
from ipray4u import limiter
from ipray4u.supabase_client import get_supabase
from ipray4u.db.profiles import ensure_profile_exists

MIN_PASSWORD_LENGTH = 8
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
INVALID_EMAIL_MESSAGE = "Enter a valid email address."
PASSWORD_RESET_SENT_MESSAGE = (
    "If an account exists for that email, a password reset link has been sent. "
    "Please check your inbox and spam folder."
)
PASSWORD_RESET_RATE_LIMIT_MESSAGE = (
    "Too many password reset requests. Please wait before trying again."
)
PASSWORD_RESET_ERROR_MESSAGE = (
    "This password reset link is invalid or has expired. "
    "Please request a new reset link."
)
PASSWORD_RESET_TOKEN_HASH_KEY = "password_reset_token_hash"

auth_blueprint = Blueprint("auth", __name__)

def normalize_email(value: str) -> str:
    return value.strip().casefold()

def is_valid_email(email: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(email))

def get_password_reset_email_key() -> str:
    email = normalize_email(request.form.get("email", ""))
    email_hash = hashlib.sha256(email.encode("utf-8")).hexdigest()
    return f"password-reset-email:{email_hash}"

@auth_blueprint.after_request
def prevent_auth_response_caching(response):
    response.headers["Cache-Control"] = "no-store"
    return response

@auth_blueprint.get("/verify")
def verify_page():
    return render_template("verify.html")

@auth_blueprint.get("/signup")
def signup_page():
    return render_template("signup.html")

@auth_blueprint.post("/signup")
def signup_user():   
    email = normalize_email(request.form.get("email", ""))
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm-password", "")

    if not is_valid_email(email):
        flash(INVALID_EMAIL_MESSAGE, "error")
        return render_template("signup.html", email=email), 400
    
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "error")
        return render_template("signup.html", email=email), 400
    
    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("signup.html", email=email), 400

    supabase = get_supabase()
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

@auth_blueprint.get("/forgot-password")
def forgot_password_page():
    return render_template("forgot-password.html")

@auth_blueprint.post("/forgot-password")
@limiter.limit("5 per hour", error_message=PASSWORD_RESET_RATE_LIMIT_MESSAGE)
@limiter.limit(
    "1 per minute",
    key_func=get_password_reset_email_key,
    error_message=PASSWORD_RESET_RATE_LIMIT_MESSAGE,
    deduct_when=lambda response: response.status_code < 400,
)
def forgot_password():
    email = normalize_email(request.form.get("email", ""))

    if not is_valid_email(email):
        flash(INVALID_EMAIL_MESSAGE, "error")
        return render_template("forgot-password.html", email=email), 400

    session.pop(PASSWORD_RESET_TOKEN_HASH_KEY, None)
    reset_url = (
        f"{current_app.config['APP_BASE_URL'].rstrip('/')}"
        f"{url_for('auth.reset_password_page')}"
    )

    try:
        get_supabase().auth.reset_password_for_email(
            email,
            {"redirect_to": reset_url},
        )
    except Exception:
        # The response must remain identical so it cannot reveal account existence.
        current_app.logger.exception("Unable to send password reset email")

    flash(PASSWORD_RESET_SENT_MESSAGE, "success")
    return redirect(url_for("auth.forgot_password_page"))

#TODO: Improve password recovery UX:
# Verify recovery tokens before displaying the reset-password form
# so expired, reused, or invalid links redirect immediately to Forgot Password page
# instead of allowing password entry only to reject it afterwards.
 
@auth_blueprint.get("/reset-password")
def reset_password_page():
    token_hash = request.args.get("token_hash", "").strip()
    recovery_type = request.args.get("type", "").strip()

    if token_hash or recovery_type:
        if not token_hash or recovery_type != "recovery":
            session.pop(PASSWORD_RESET_TOKEN_HASH_KEY, None)
            flash(PASSWORD_RESET_ERROR_MESSAGE, "error")
            return redirect(url_for("auth.forgot_password_page"))

        session[PASSWORD_RESET_TOKEN_HASH_KEY] = token_hash
        return redirect(url_for("auth.reset_password_page"))

    if not session.get(PASSWORD_RESET_TOKEN_HASH_KEY):
        flash(PASSWORD_RESET_ERROR_MESSAGE, "error")
        return redirect(url_for("auth.forgot_password_page"))

    return render_template("reset-password.html")

@auth_blueprint.post("/reset-password")
def reset_password():
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm-password", "")
    token_hash = session.get(PASSWORD_RESET_TOKEN_HASH_KEY)

    if not password or len(password) < MIN_PASSWORD_LENGTH:
        flash(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.", "error")
        return render_template("reset-password.html"), 400

    if password != confirm_password:
        flash("Passwords do not match.", "error")
        return render_template("reset-password.html"), 400

    if not token_hash:
        flash(PASSWORD_RESET_ERROR_MESSAGE, "error")
        return redirect(url_for("auth.forgot_password_page"))

    try:
        supabase = get_supabase()
        response = supabase.auth.verify_otp(
            {
                "token_hash": token_hash,
                "type": "recovery",
            }
        )
        if not response.session:
            raise RuntimeError("Password recovery session was not returned")

        supabase.auth.update_user({"password": password})
    except Exception:
        current_app.logger.exception("Unable to reset password")
        session.pop(PASSWORD_RESET_TOKEN_HASH_KEY, None)
        flash(PASSWORD_RESET_ERROR_MESSAGE, "error")
        return redirect(url_for("auth.forgot_password_page"))

    session.pop(PASSWORD_RESET_TOKEN_HASH_KEY, None)
    try:
        supabase.auth.sign_out({"scope": "local"})
    except Exception:
        current_app.logger.exception("Unable to clear password recovery session")

    flash("Password updated. You can now log in.", "success")
    return redirect(url_for("auth.login_page"))

@auth_blueprint.post("/login")
def login_user():
    supabase = get_supabase()
    email = normalize_email(request.form.get("email", ""))

    if not is_valid_email(email):
        flash("Invalid email or password.", "error")
        return render_template("login.html", email=email), 401
    
    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": email,
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
        return render_template("login.html", email=email), 401
    
    except Exception:
        current_app.logger.exception("Unexpected error during login")
        flash("Something went wrong. Please try again.", "error")
        return redirect(url_for("auth.login_page"))

@auth_blueprint.post("/logout")
def logout_user():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login_page"))
