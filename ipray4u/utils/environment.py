import os 

TEST_REQUIRED_ENV_VARS = [
  "APP_BASE_URL",
  "TEST_DATABASE_URL",
  "SECRET_KEY",
  "SESSION_COOKIE_SECURE",
]

APP_REQUIRED_ENV_VARS = [
  "APP_ENV",
  "APP_BASE_URL",
  "DATABASE_URL",
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "RATELIMIT_STORAGE_URI",
  "SECRET_KEY",
  "SESSION_COOKIE_SECURE",
]

def validate_required_env_vars(required_vars):
  missing_vars = [v for v in required_vars if not os.environ.get(v)]
  
  if missing_vars:
    raise RuntimeError(
      f"Missing required environment variables: {', '.join(missing_vars)}"
    )

  if required_vars is APP_REQUIRED_ENV_VARS:
    validate_app_env()
    get_trusted_proxy_count()

def get_app_env():
  return os.environ.get("APP_ENV", "").strip().lower()

def validate_app_env():
  app_env = get_app_env()

  if app_env not in {"local", "staging", "production"}:
    raise RuntimeError(
      "APP_ENV must be one of 'local', 'staging', or 'production'."
    )

def is_production():
  return get_app_env() == "production"

def is_staging():
  return get_app_env() == "staging"

def is_deployed_environment():
  return is_production() or is_staging()

def get_ratelimit_storage_uri():
  storage_uri = os.environ.get("RATELIMIT_STORAGE_URI")

  if not is_deployed_environment():
    return storage_uri.strip() if storage_uri else "memory://"

  storage_uri = storage_uri.strip() if storage_uri else ""

  if not storage_uri or storage_uri.lower() == "memory://":
    raise RuntimeError(
      "RATELIMIT_STORAGE_URI must be configured with a shared Redis/Valkey "
      "backend when APP_ENV is 'staging' or 'production'."
    )

  return storage_uri

def parse_trusted_proxy_count(raw_value):
  try:
    proxy_count = int(raw_value)
  except (TypeError, ValueError) as error:
    raise RuntimeError("TRUSTED_PROXY_COUNT must be a non-negative integer.") from error

  if proxy_count < 0:
    raise RuntimeError("TRUSTED_PROXY_COUNT must be a non-negative integer.")

  return proxy_count

def get_trusted_proxy_count():
  raw_value = os.environ.get("TRUSTED_PROXY_COUNT")

  if raw_value is None:
    if is_deployed_environment():
      raise RuntimeError(
        "TRUSTED_PROXY_COUNT must be configured in deployed environments."
      )

    return 0

  return parse_trusted_proxy_count(raw_value)
