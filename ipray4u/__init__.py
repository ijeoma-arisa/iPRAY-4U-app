import os
from flask import (
  Flask,
  g,
  render_template,
)
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from .db import init_db
from .utils.environment import (
  TEST_REQUIRED_ENV_VARS,
  PROD_REQUIRED_ENV_VARS,
  validate_required_env_vars,
)

load_dotenv()

csrf = CSRFProtect()

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  
  required_env_vars = TEST_REQUIRED_ENV_VARS if test_config else PROD_REQUIRED_ENV_VARS
  validate_required_env_vars(required_env_vars)
  
  app.config.from_mapping(
    DATABASE_URL=os.environ.get("DATABASE_URL"),
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
  
  csrf.init_app(app)
  
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
    
  with app.app_context():
    init_db()

  @app.teardown_appcontext
  def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
      db.close()

  return app