import os 

def validate_required_env_vars(required_vars):
  missing_vars = [v for v in required_vars if not os.environ.get(v)]
  
  if missing_vars:
    raise RuntimeError(
      f"Missing required environment variables: {','.join(missing_vars)}"
    )