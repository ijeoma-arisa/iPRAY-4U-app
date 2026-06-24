import pytest
from ipray4u.utils.environment import validate_required_env_vars

REQUIRED_ENV_VARS = [
  "DATABASE_URL",
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "SECRET_KEY",
]

def test_validate_required_env_vars_passes_when_all_vars_exist(monkeypatch):
    for var in REQUIRED_ENV_VARS:
        monkeypatch.setenv(var, "test-value")
        
    validate_required_env_vars(REQUIRED_ENV_VARS)


def test_validate_required_env_vars_raises_when_var_is_missing(monkeypatch):
    for var in REQUIRED_ENV_VARS:
        monkeypatch.setenv(var, "test-value")
        
    monkeypatch.delenv("SECRET_KEY")
    
    with pytest.raises(RuntimeError) as error:
        validate_required_env_vars(REQUIRED_ENV_VARS)
    
    assert "SECRET_KEY" in str(error.value)
