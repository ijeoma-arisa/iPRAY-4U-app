from functools import wraps
from flask import session, flash, redirect, url_for
from ipray4u.responses import error_json
from ipray4u.utils.error_messages import AUTHENTICATION_REQUIRED_ERROR 

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
            return error_json(AUTHENTICATION_REQUIRED_ERROR), 401
        
        return f(*args, **kwargs)
    return wrapper


