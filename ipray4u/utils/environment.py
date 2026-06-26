import os 

TEST_REQUIRED_ENV_VARS = [
  "TEST_DATABASE_URL",
  "SECRET_KEY",
  "SESSION_COOKIE_SECURE",
]

PROD_REQUIRED_ENV_VARS = [
  "DATABASE_URL",
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "SECRET_KEY",
  "SESSION_COOKIE_SECURE",
]

def validate_required_env_vars(required_vars):
  missing_vars = [v for v in required_vars if not os.environ.get(v)]
  
  if missing_vars:
    raise RuntimeError(
      f"Missing required environment variables: {', '.join(missing_vars)}"
    )
    