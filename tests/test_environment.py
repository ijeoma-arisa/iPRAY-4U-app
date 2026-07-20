import os
import pytest
from flask import request
from werkzeug.middleware.proxy_fix import ProxyFix
from ipray4u import create_app, limiter
from ipray4u.utils.environment import (
    APP_REQUIRED_ENV_VARS,
    get_ratelimit_storage_uri,
    get_trusted_proxy_count,
    get_app_env,
    is_production,
    is_staging,
    validate_required_env_vars,
)

VALID_LOCAL_APP_ENV_VALUES = {
    "APP_ENV": "local",
    "APP_BASE_URL": "http://localhost:5000",
    "DATABASE_URL": "postgresql://user:password@localhost/test",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_PUBLISHABLE_KEY": "test-key",
    "RATELIMIT_STORAGE_URI": "memory://",
    "SECRET_KEY": "test-secret",
    "SESSION_COOKIE_SECURE": "False",
}

REQUIRED_ENV_VALUES = {
    "APP_BASE_URL": "https://test.ipray4u.example",
    "DATABASE_URL": "postgresql://user:password@localhost/test",
    "SUPABASE_URL": "https://test.supabase.co",
    "SUPABASE_PUBLISHABLE_KEY": "test-key",
    "SECRET_KEY": "test-secret",
}


def set_env_values(monkeypatch, values):
    for name, value in values.items():
        monkeypatch.setenv(name, value)

def test_validate_required_env_vars_passes_when_all_vars_exist(monkeypatch):
    set_env_values(monkeypatch, REQUIRED_ENV_VALUES)

    validate_required_env_vars(list(REQUIRED_ENV_VALUES))


def test_validate_required_env_vars_raises_when_var_is_missing(monkeypatch):
    set_env_values(monkeypatch, REQUIRED_ENV_VALUES)
    monkeypatch.delenv("SECRET_KEY")
    
    with pytest.raises(RuntimeError) as error:
        validate_required_env_vars(list(REQUIRED_ENV_VALUES))
    
    assert "SECRET_KEY" in str(error.value)


def test_create_app_raises_when_app_base_url_is_missing(monkeypatch):
    monkeypatch.delenv("APP_BASE_URL")

    with pytest.raises(RuntimeError) as error:
        create_app({
            "RATELIMIT_STORAGE_URI": "memory://",
            "TESTING": True,
        })

    assert "APP_BASE_URL" in str(error.value)


def test_ratelimit_storage_defaults_to_memory_outside_deployed_env(monkeypatch):
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)

    assert get_ratelimit_storage_uri() == "memory://"


def test_production_env_is_detected(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")

    assert is_production()


def test_staging_env_is_detected(monkeypatch):
    monkeypatch.setenv("APP_ENV", "staging")

    assert is_staging()


def test_app_env_rejects_missing_or_invalid_value(monkeypatch):
    set_env_values(monkeypatch, VALID_LOCAL_APP_ENV_VALUES)

    monkeypatch.delenv("APP_ENV", raising=False)

    with pytest.raises(RuntimeError) as missing_error:
        validate_required_env_vars(APP_REQUIRED_ENV_VARS)

    assert "APP_ENV" in str(missing_error.value)

    monkeypatch.setenv("APP_ENV", "development")

    with pytest.raises(RuntimeError) as invalid_error:
        validate_required_env_vars(APP_REQUIRED_ENV_VARS)

    assert "APP_ENV" in str(invalid_error.value)


def test_app_required_env_vars_allow_local_environment(monkeypatch):
    set_env_values(monkeypatch, VALID_LOCAL_APP_ENV_VALUES)

    validate_required_env_vars(APP_REQUIRED_ENV_VARS)


def test_app_env_returns_normalized_value(monkeypatch):
    monkeypatch.setenv("APP_ENV", " Production ")

    assert get_app_env() == "production"


def test_create_app_allows_test_config_memory_storage_in_production(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)

    app = create_app({
        "APP_BASE_URL": "https://test.ipray4u.example",
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": False,
        "RATELIMIT_STORAGE_URI": "memory://",
        "TESTING": True,
        "TRUSTED_PROXY_COUNT": "2",
        "WTF_CSRF_ENABLED": False,
    })

    assert app.config["RATELIMIT_STORAGE_URI"] == "memory://"


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_ratelimit_storage_rejects_missing_uri_in_deployed_env(
    monkeypatch, app_env
):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)

    with pytest.raises(RuntimeError) as error:
        get_ratelimit_storage_uri()

    assert "RATELIMIT_STORAGE_URI" in str(error.value)


def test_create_app_requires_ratelimit_storage_uri_for_production(monkeypatch):
    set_env_values(monkeypatch, REQUIRED_ENV_VALUES)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")
    monkeypatch.delenv("RATELIMIT_STORAGE_URI", raising=False)

    with pytest.raises(RuntimeError) as error:
        create_app()

    assert "RATELIMIT_STORAGE_URI" in str(error.value)


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_ratelimit_storage_rejects_blank_uri_in_deployed_env(
    monkeypatch, app_env
):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", " ")

    with pytest.raises(RuntimeError) as error:
        get_ratelimit_storage_uri()

    assert "RATELIMIT_STORAGE_URI" in str(error.value)


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_ratelimit_storage_rejects_memory_uri_in_deployed_env(
    monkeypatch, app_env
):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")

    with pytest.raises(RuntimeError) as error:
        get_ratelimit_storage_uri()

    assert "RATELIMIT_STORAGE_URI" in str(error.value)


def test_create_app_rejects_memory_ratelimit_storage_in_production(monkeypatch):
    set_env_values(monkeypatch, REQUIRED_ENV_VALUES)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "memory://")
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "2")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")

    with pytest.raises(RuntimeError) as error:
        create_app()

    assert "RATELIMIT_STORAGE_URI" in str(error.value)


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_ratelimit_storage_allows_shared_backend_in_deployed_env(
    monkeypatch, app_env
):
    monkeypatch.setenv("APP_ENV", app_env)
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://localhost:6379/0")

    assert get_ratelimit_storage_uri() == "redis://localhost:6379/0"


def test_create_app_requires_trusted_proxy_count_for_production(monkeypatch):
    set_env_values(monkeypatch, REQUIRED_ENV_VALUES)

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("RATELIMIT_STORAGE_URI", "redis://localhost:6379/0")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "true")
    monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)

    with pytest.raises(RuntimeError) as error:
        create_app()

    assert "TRUSTED_PROXY_COUNT" in str(error.value)


def test_trusted_proxy_count_defaults_to_zero_outside_deployed_env(monkeypatch):
    monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    assert get_trusted_proxy_count() == 0


def test_local_trusted_proxy_count_can_be_zero(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "0")

    assert get_trusted_proxy_count() == 0


def test_local_trusted_proxy_count_defaults_to_zero(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)

    assert get_trusted_proxy_count() == 0


@pytest.mark.parametrize("app_env", ["staging", "production"])
def test_trusted_proxy_count_is_required_in_deployed_environment(
    monkeypatch, app_env
):
    monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)
    monkeypatch.setenv("APP_ENV", app_env)

    with pytest.raises(RuntimeError) as error:
        get_trusted_proxy_count()

    assert "TRUSTED_PROXY_COUNT" in str(error.value)


def test_trusted_proxy_count_allows_render_two_proxy_hops(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "2")

    assert get_trusted_proxy_count() == 2


@pytest.mark.parametrize("value", ["", "invalid", "1.5"])
def test_trusted_proxy_count_rejects_non_integer_value(monkeypatch, value):
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", value)

    with pytest.raises(RuntimeError) as error:
        get_trusted_proxy_count()

    assert "TRUSTED_PROXY_COUNT" in str(error.value)


def test_trusted_proxy_count_rejects_negative_value(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "-1")

    with pytest.raises(RuntimeError) as error:
        get_trusted_proxy_count()

    assert "TRUSTED_PROXY_COUNT" in str(error.value)


def test_proxy_fix_uses_x_forwarded_for_when_configured(monkeypatch):
    monkeypatch.setenv("TRUSTED_PROXY_COUNT", "2")

    app = create_app({
        "APP_BASE_URL": "https://test.ipray4u.example",
        "TESTING": True,
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": False,
        "RATELIMIT_STORAGE_URI": "memory://",
        "WTF_CSRF_ENABLED": False,
    })

    @app.get("/remote-addr-test")
    def remote_addr_test():
        return {
            "is_secure": request.is_secure,
            "remote_addr": request.remote_addr,
            "scheme": request.scheme,
        }

    client = app.test_client()
    response = client.get(
        "/remote-addr-test",
        environ_base={"REMOTE_ADDR": "10.0.0.5"},
        headers={
            "X-Forwarded-For": "203.0.113.10, 10.0.0.10",
            "X-Forwarded-Proto": "https",
        },
    )

    assert response.get_json() == {
        "is_secure": True,
        "remote_addr": "203.0.113.10",
        "scheme": "https",
    }


@pytest.mark.parametrize("proxy_value", [None, "0"])
def test_local_zero_proxy_count_does_not_apply_proxy_fix(
    monkeypatch, proxy_value
):
    monkeypatch.setenv("APP_ENV", "local")
    if proxy_value is None:
        monkeypatch.delenv("TRUSTED_PROXY_COUNT", raising=False)
    else:
        monkeypatch.setenv("TRUSTED_PROXY_COUNT", proxy_value)

    app = create_app({
        "APP_BASE_URL": "http://localhost:5000",
        "TESTING": True,
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": False,
        "RATELIMIT_STORAGE_URI": "memory://",
        "WTF_CSRF_ENABLED": False,
    })

    assert app.config["APP_ENV"] == "local"
    assert app.config["TRUSTED_PROXY_COUNT"] == 0
    assert not isinstance(app.wsgi_app, ProxyFix)


def test_rate_limit_blocks_after_configured_limit():
    app = create_app({
        "APP_BASE_URL": "https://test.ipray4u.example",
        "TESTING": True,
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": True,
        "RATELIMIT_STORAGE_URI": "memory://",
        "WTF_CSRF_ENABLED": False,
    })

    @app.get("/rate-limit-test")
    @limiter.limit("2 per minute")
    def rate_limit_test():
        return {"ok": True}

    client = app.test_client()

    limiter.reset()

    try:
        assert client.get("/rate-limit-test").status_code == 200
        assert client.get("/rate-limit-test").status_code == 200
        assert client.get("/rate-limit-test").status_code == 429
    finally:
        limiter.reset()
