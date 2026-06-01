import os
from flask import Flask, g
from dotenv import load_dotenv
from .db import init_db

load_dotenv()

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  
  app.config.from_mapping(
    DATABASE_URL=os.environ.get("DATABASE_URL"),
    SECRET_KEY=os.environ.get("SECRET_KEY"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False, # True in production later
    SESSION_COOKIE_SAMESITE="Lax",
  )
  
  if test_config:
    app.config.update(test_config)
  
  if not app.config.get("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not configured.")
  
  # if not app.config.get("SECRET_KEY"):
    # raise RuntimeError("SECRET_KEY is not configured.")
  
  
  from ipray4u.routes.auth import auth_blueprint
  from ipray4u.routes.pages import pages_blueprint
  from ipray4u.routes.people import people_blueprint
  from ipray4u.routes.prayers import prayers_blueprint
  from ipray4u.routes.relationships import relationships_blueprint
  
  app.register_blueprint(auth_blueprint)
  app.register_blueprint(pages_blueprint)
  app.register_blueprint(people_blueprint)
  app.register_blueprint(prayers_blueprint)
  app.register_blueprint(relationships_blueprint)
  
  with app.app_context():
    init_db()
    
  @app.teardown_appcontext
  def close_db_connection(exception):
    db = g.pop("db", None)
    if db is not None:
      db.close()

  return app