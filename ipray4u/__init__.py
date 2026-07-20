import os
from flask import (
  Flask,
  flash,
  g,
  render_template,
  session,
)
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.middleware.proxy_fix import ProxyFix
from .db import init_db
from .utils.environment import (
  TEST_REQUIRED_ENV_VARS,
  APP_REQUIRED_ENV_VARS,
  get_app_env,
  get_ratelimit_storage_uri,
  get_trusted_proxy_count,
  parse_trusted_proxy_count,
  validate_required_env_vars,
)

load_dotenv()

csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address)

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  
  required_env_vars = TEST_REQUIRED_ENV_VARS if test_config else APP_REQUIRED_ENV_VARS
  validate_required_env_vars(required_env_vars)
  test_ratelimit_storage_uri = None

  if test_config and "RATELIMIT_STORAGE_URI" in test_config:
    test_ratelimit_storage_uri = test_config["RATELIMIT_STORAGE_URI"]

  ratelimit_storage_uri = (
    test_ratelimit_storage_uri
    if test_ratelimit_storage_uri is not None
    else get_ratelimit_storage_uri()
  )
  
  app.config.from_mapping(
    APP_ENV=get_app_env(),
    APP_BASE_URL=os.environ["APP_BASE_URL"],
    DATABASE_URL=os.environ.get("DATABASE_URL"),
    RATELIMIT_STORAGE_URI=ratelimit_storage_uri,
    SECRET_KEY=os.environ.get("SECRET_KEY"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=(
      os.environ["SESSION_COOKIE_SECURE"].lower() == "true"
    ),
    SESSION_COOKIE_SAMESITE="Lax",
  )
  
  if test_config:
    app.config.update(test_config)
  
  if not app.config.get("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not configured.")
  
  if not app.config.get("SECRET_KEY"):
    raise RuntimeError("SECRET_KEY is not configured.")

  trusted_proxy_count = app.config.get("TRUSTED_PROXY_COUNT")

  if trusted_proxy_count is None:
    trusted_proxy_count = get_trusted_proxy_count()
  else:
    trusted_proxy_count = parse_trusted_proxy_count(trusted_proxy_count)

  app.config["TRUSTED_PROXY_COUNT"] = trusted_proxy_count

  if trusted_proxy_count > 0:
    app.wsgi_app = ProxyFix(
      app.wsgi_app,
      x_for=trusted_proxy_count,
      # Header trust counts are independent; Render has two forwarded address
      # values, but only one verified forwarded proto value so far.
      x_proto=1,
    )
  
  csrf.init_app(app)
  limiter.init_app(app)
  
  from ipray4u.routes import (
    auth_blueprint,
    pages_blueprint,
    people_blueprint,
    prayers_blueprint,
    relationships_blueprint
  )
  
  app.register_blueprint(auth_blueprint)
  app.register_blueprint(pages_blueprint)
  app.register_blueprint(people_blueprint)
  app.register_blueprint(prayers_blueprint)
  app.register_blueprint(relationships_blueprint)
  
  @app.errorhandler(500)
  def internal_server_error(error):
    return render_template("500.html"), 500

  @app.errorhandler(429)
  def too_many_requests(error):
    from ipray4u.routes.auth import PASSWORD_RESET_RATE_LIMIT_MESSAGE

    # This is correct while forgot password is the only rate-limited endpoint.
    # Expand this handler if other flows start using rate limits.
    session.pop("_flashes", None)
    flash(PASSWORD_RESET_RATE_LIMIT_MESSAGE, "error")
    return render_template("forgot-password.html"), 429
    
  with app.app_context():
    init_db()

  @app.teardown_appcontext
  def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
      db.close()

  return app
