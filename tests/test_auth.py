import os

from .helpers.assertions import assert_success_response
from ipray4u import create_app, limiter
from ipray4u.utils.success_messages import get_success
from ipray4u.routes.auth import (
    INVALID_EMAIL_MESSAGE,
    PASSWORD_RESET_ERROR_MESSAGE,
    PASSWORD_RESET_RATE_LIMIT_MESSAGE,
    PASSWORD_RESET_SENT_MESSAGE,
    PASSWORD_RESET_TOKEN_HASH_KEY,
    get_password_reset_email_key,
)
from .helpers.urls import (
    SIGNUP_URL,
    VERIFY_URL,
    LOGIN_URL,
    LOGOUT_URL, 
    FORGOT_PASSWORD_URL,
    RESET_PASSWORD_URL,
    PRAYER_REQUESTS_URL,
)

# Signup Tests
# TODO: Add signup validation tests:
# - password mismatch
# - password too short
# - verify sign_up is not called on validation failure
    
def test_signup_page_loads(client):
    response = client.get(SIGNUP_URL)
    
    assert response.status_code == 200
    assert b"Sign Up" in response.data
    assert response.data.count(
        b'data-password-toggle="password confirm-password"'
    ) == 2
    assert b">Show<" not in response.data

def test_signup_with_valid_data_redirects_to_verify_page(
    client, 
    auth_form_data,
    mock_supabase,
    ):

    response = client.post(SIGNUP_URL, data=auth_form_data)
    
    assert response.status_code == 302
    assert response.headers["Location"] == VERIFY_URL
    
    mock_supabase.auth.sign_up.assert_called_once_with({
        "email": auth_form_data["email"],
        "password": auth_form_data["password"],
    })


def test_signup_normalizes_email_before_sending_to_supabase(
    client,
    auth_form_data,
    mock_supabase,
):
    auth_form_data["email"] = "  PERSON@EXAMPLE.COM  "

    response = client.post(SIGNUP_URL, data=auth_form_data)

    assert response.status_code == 302
    mock_supabase.auth.sign_up.assert_called_once_with({
        "email": "person@example.com",
        "password": auth_form_data["password"],
    })


def test_signup_rejects_invalid_email(client, auth_form_data, mock_supabase):
    auth_form_data["email"] = "  NOT-AN-EMAIL  "

    response = client.post(SIGNUP_URL, data=auth_form_data)

    assert response.status_code == 400
    assert INVALID_EMAIL_MESSAGE.encode() in response.data
    assert b'value="not-an-email"' in response.data
    assert b'value="test-password"' not in response.data
    mock_supabase.auth.sign_up.assert_not_called()


def test_signup_rejects_empty_email(client, auth_form_data, mock_supabase):
    auth_form_data["email"] = " "

    response = client.post(SIGNUP_URL, data=auth_form_data)

    assert response.status_code == 400
    assert INVALID_EMAIL_MESSAGE.encode() in response.data
    mock_supabase.auth.sign_up.assert_not_called()
    

# TODO: Add tests for verify.html / email verification flow
    
# Login Tests
def test_login_page_loads(client):
    response = client.get(LOGIN_URL)
    
    assert response.status_code == 200
    assert b"Log In" in response.data
    assert b'data-password-toggle="password"' in response.data
    assert b">Show<" not in response.data


def test_login_with_valid_credentials_sets_session_and_redirects(
    client,
    mock_login_response,
    auth_form_data,
    mock_supabase,
    ):
    
    mock_supabase.auth.sign_in_with_password.return_value = mock_login_response
    
    response = client.post(LOGIN_URL, data=auth_form_data)
    
    assert response.status_code == 302
    assert response.headers["Location"] == PRAYER_REQUESTS_URL
    
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({
        "email": auth_form_data["email"],
        "password": auth_form_data["password"],
    })
    
    with client.session_transaction() as session:
        assert session["user_id"] == mock_login_response.user.id
        assert session["email"] == mock_login_response.user.email


def test_login_normalizes_email_before_sending_credentials(
    client,
    mock_login_response,
    auth_form_data,
    mock_supabase,
):
    auth_form_data["email"] = "  TEST@example.com  "
    mock_supabase.auth.sign_in_with_password.return_value = mock_login_response

    response = client.post(LOGIN_URL, data=auth_form_data)

    assert response.status_code == 302
    mock_supabase.auth.sign_in_with_password.assert_called_once_with({
        "email": "test@example.com",
        "password": auth_form_data["password"],
    })


def test_login_with_invalid_credentials_rerenders_login_and_does_not_set_session(
    client, 
    auth_form_data,
    mock_supabase,
    mocker,
    ):
    
    class FakeAuthApiError(Exception):
        pass
    
    mocker.patch("ipray4u.routes.auth.AuthApiError", FakeAuthApiError)
    
    mock_supabase.auth.sign_in_with_password.side_effect = FakeAuthApiError()
    
    auth_form_data["email"] = "  TEST@example.com  "

    response = client.post(LOGIN_URL, data=auth_form_data)
    
    assert response.status_code == 401
    assert b"Invalid email or password" in response.data
    assert b'value="test@example.com"' in response.data
    assert b'value="test-password"' not in response.data
    
    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session


def test_login_rejects_malformed_email_without_calling_supabase(
    client,
    auth_form_data,
    mock_supabase,
):
    auth_form_data["email"] = "  NOT-AN-EMAIL  "

    response = client.post(LOGIN_URL, data=auth_form_data)

    assert response.status_code == 401
    assert b"Invalid email or password." in response.data
    assert b'value="not-an-email"' in response.data
    assert b"value=\"test-password\"" not in response.data
    mock_supabase.auth.sign_in_with_password.assert_not_called()


def test_login_rejects_empty_email_without_calling_supabase(
    client,
    auth_form_data,
    mock_supabase,
):
    auth_form_data["email"] = " "

    response = client.post(LOGIN_URL, data=auth_form_data)

    assert response.status_code == 401
    assert b"Invalid email or password." in response.data
    assert b'value=""' in response.data
    assert b"value=\"test-password\"" not in response.data
    mock_supabase.auth.sign_in_with_password.assert_not_called()


def test_login_with_unexpected_error_redirects_to_login_and_does_not_set_session(
    client,
    auth_form_data,
    mock_supabase,
    ):
    mock_supabase.auth.sign_in_with_password.side_effect = Exception("Network error")
    
    response = client.post(LOGIN_URL, data=auth_form_data)
    
    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL
    
    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session


# Password Reset Tests
def test_forgot_password_page_loads(client):
    response = client.get(FORGOT_PASSWORD_URL)

    assert response.status_code == 200
    assert b"Forgot Password" in response.data
    assert b"forgot-password.js" in response.data


def test_forgot_password_script_loads(client):
    response = client.get("/static/js/forgot-password.js")

    assert response.status_code == 200


def test_reset_password_page_loads(client):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    response = client.get(RESET_PASSWORD_URL)

    assert response.status_code == 200
    assert b"Reset Password" in response.data
    assert response.data.count(
        b'data-password-toggle="password confirm-password"'
    ) == 2
    assert b">Show<" not in response.data


def test_forgot_password_sends_reset_email(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "stale-token"

    response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "  PERSON@example.com  "},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == FORGOT_PASSWORD_URL
    mock_supabase.auth.reset_password_for_email.assert_called_once_with(
        "person@example.com",
        {"redirect_to": "https://test.ipray4u.example/reset-password"},
    )

    with client.session_transaction() as flask_session:
        assert PASSWORD_RESET_TOKEN_HASH_KEY not in flask_session


def test_forgot_password_rejects_invalid_email_and_preserves_value(
    client,
    mock_supabase,
):
    response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "  BAD-EMAIL  "},
    )

    assert response.status_code == 400
    assert INVALID_EMAIL_MESSAGE.encode() in response.data
    assert b'value="bad-email"' in response.data
    mock_supabase.auth.reset_password_for_email.assert_not_called()


def test_forgot_password_rejects_empty_email(client, mock_supabase):
    response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": " "},
    )

    assert response.status_code == 400
    assert INVALID_EMAIL_MESSAGE.encode() in response.data
    mock_supabase.auth.reset_password_for_email.assert_not_called()


def test_forgot_password_success_message_mentions_spam_folder(
    client,
    mock_supabase,
):
    response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "person@example.com"},
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert PASSWORD_RESET_SENT_MESSAGE.encode() in response.data
    assert b"spam folder" in response.data


def test_password_reset_email_rate_limit_key_hashes_normalized_email(app):
    with app.test_request_context(
        FORGOT_PASSWORD_URL,
        method="POST",
        data={"email": "  PERSON@example.com  "},
    ):
        key = get_password_reset_email_key()

    with app.test_request_context(
        FORGOT_PASSWORD_URL,
        method="POST",
        data={"email": "person@example.com"},
    ):
        normalized_key = get_password_reset_email_key()

    assert key == normalized_key
    assert "person@example.com" not in key
    assert key.startswith("password-reset-email:")


def test_auth_responses_are_not_cached(client):
    response = client.get(FORGOT_PASSWORD_URL)

    assert response.headers["Cache-Control"] == "no-store"


def test_forgot_password_does_not_reveal_account_existence(
    client,
    mock_supabase,
):
    successful_response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "person@example.com"},
        follow_redirects=True,
    )

    mock_supabase.auth.reset_password_for_email.side_effect = Exception(
        "User not found"
    )

    missing_account_response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "missing@example.com"},
        follow_redirects=True,
    )

    assert missing_account_response.status_code == 200
    assert missing_account_response.data == successful_response.data
    assert PASSWORD_RESET_SENT_MESSAGE.encode() in missing_account_response.data
    assert b"missing@example.com" not in missing_account_response.data
    assert b"User not found" not in missing_account_response.data


def test_forgot_password_is_rate_limited(mock_supabase):
    app = create_app({
        "APP_BASE_URL": "https://test.ipray4u.example",
        "TESTING": True,
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": True,
        "RATELIMIT_STORAGE_URI": "memory://",
        "WTF_CSRF_ENABLED": False,
    })
    client = app.test_client()

    limiter.reset()

    try:
        responses = [
            client.post(
                FORGOT_PASSWORD_URL,
                data={"email": f"person-{index}@example.com"},
            )
            for index in range(6)
        ]
    finally:
        limiter.reset()

    assert all(response.status_code == 302 for response in responses[:5])
    assert responses[5].status_code == 429
    assert b"Forgot Password" in responses[5].data
    assert PASSWORD_RESET_RATE_LIMIT_MESSAGE.encode() in responses[5].data
    assert mock_supabase.auth.reset_password_for_email.call_count == 5


def test_forgot_password_is_rate_limited_by_email(mock_supabase):
    app = create_app({
        "APP_BASE_URL": "https://test.ipray4u.example",
        "TESTING": True,
        "DATABASE_URL": os.environ["TEST_DATABASE_URL"],
        "RATELIMIT_ENABLED": True,
        "RATELIMIT_STORAGE_URI": "memory://",
        "WTF_CSRF_ENABLED": False,
    })
    client = app.test_client()

    limiter.reset()

    try:
        first_response = client.post(
            FORGOT_PASSWORD_URL,
            data={"email": "  PERSON@example.com  "},
        )
        second_response = client.post(
            FORGOT_PASSWORD_URL,
            data={"email": "person@example.com"},
        )
    finally:
        limiter.reset()

    assert first_response.status_code == 302
    assert second_response.status_code == 429
    assert PASSWORD_RESET_RATE_LIMIT_MESSAGE.encode() in second_response.data
    mock_supabase.auth.reset_password_for_email.assert_called_once()


def test_reset_password_stores_recovery_token_hash(client, mock_supabase):
    response = client.get(
        f"{RESET_PASSWORD_URL}?token_hash=recovery-token&type=recovery"
    )

    assert response.status_code == 302
    assert response.headers["Location"] == RESET_PASSWORD_URL

    with client.session_transaction() as flask_session:
        assert flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] == "recovery-token"

    mock_supabase.auth.verify_otp.assert_not_called()


def test_reset_password_rejects_invalid_recovery_type(client):
    response = client.get(
        f"{RESET_PASSWORD_URL}?token_hash=recovery-token&type=invite",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert PASSWORD_RESET_ERROR_MESSAGE.encode() in response.data


def test_reset_password_page_redirects_without_recovery_token(client):
    response = client.get(RESET_PASSWORD_URL, follow_redirects=True)

    assert response.status_code == 200
    assert b"Forgot Password" in response.data
    assert PASSWORD_RESET_ERROR_MESSAGE.encode() in response.data


def test_reset_password_missing_recovery_session_does_not_update_user(
    client,
    mock_supabase,
):
    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "new-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert PASSWORD_RESET_ERROR_MESSAGE.encode() in response.data
    mock_supabase.auth.verify_otp.assert_not_called()
    mock_supabase.auth.update_user.assert_not_called()


def test_reset_password_too_short_does_not_update_user(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    response = client.post(
        RESET_PASSWORD_URL,
        data={"password": "short", "confirm-password": "short"},
    )

    assert response.status_code == 400
    assert b"Password must be at least 8 characters" in response.data
    mock_supabase.auth.verify_otp.assert_not_called()
    mock_supabase.auth.update_user.assert_not_called()


def test_reset_password_mismatch_does_not_update_user(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "different-password",
        },
    )

    assert response.status_code == 400
    assert b"Passwords do not match" in response.data
    mock_supabase.auth.verify_otp.assert_not_called()
    mock_supabase.auth.update_user.assert_not_called()


def test_reset_password_updates_user_and_redirects_to_login(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    mock_supabase.auth.verify_otp.return_value.session = object()

    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "new-password",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL
    mock_supabase.auth.verify_otp.assert_called_once_with(
        {
            "token_hash": "recovery-token",
            "type": "recovery",
        }
    )
    mock_supabase.auth.update_user.assert_called_once_with(
        {"password": "new-password"}
    )
    mock_supabase.auth.sign_out.assert_called_once_with({"scope": "local"})

    with client.session_transaction() as flask_session:
        assert PASSWORD_RESET_TOKEN_HASH_KEY not in flask_session


def test_reset_password_update_failure_is_safe(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    mock_supabase.auth.verify_otp.return_value.session = object()
    mock_supabase.auth.update_user.side_effect = Exception(
        "Sensitive Supabase update error"
    )

    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "new-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert PASSWORD_RESET_ERROR_MESSAGE.encode() in response.data
    assert b"Sensitive Supabase update error" not in response.data

    with client.session_transaction() as flask_session:
        assert PASSWORD_RESET_TOKEN_HASH_KEY not in flask_session


def test_reset_password_verification_failure_is_safe(client, mock_supabase):
    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    mock_supabase.auth.verify_otp.side_effect = Exception(
        "Sensitive Supabase verification error"
    )

    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "new-password",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert PASSWORD_RESET_ERROR_MESSAGE.encode() in response.data
    assert b"Sensitive Supabase verification error" not in response.data
    mock_supabase.auth.update_user.assert_not_called()

    with client.session_transaction() as flask_session:
        assert PASSWORD_RESET_TOKEN_HASH_KEY not in flask_session

# Logout Tests
def test_logout_clears_session_and_redirects_to_login(auth_client):
    response = auth_client.post(LOGOUT_URL)
    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL
    
    with auth_client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session
        

def test_logout_makes_protected_page_inaccessible(auth_client):
    response = auth_client.get(PRAYER_REQUESTS_URL)

    assert response.status_code == 200

    auth_client.post(LOGOUT_URL)

    response = auth_client.get(PRAYER_REQUESTS_URL)

    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL


def test_logout_get_method_not_allowed(auth_client):
    response = auth_client.get(LOGOUT_URL)
    
    assert response.status_code == 405
    
# TODO: Add CSRF Tests
