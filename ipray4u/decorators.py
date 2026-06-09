from functools import wraps
from flask import session, flash, redirect, url_for
from ipray4u.responses import error_json

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue", "error")
                  
            return redirect(url_for("auth.login_page"))
        return f(*args, **kwargs)
    return wrapper

def api_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return error_json("Authentication required"), 401
        
        return f(*args, **kwargs)
    return wrapper


