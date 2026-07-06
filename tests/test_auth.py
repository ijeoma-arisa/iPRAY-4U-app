from .helpers.assertions import assert_success_response
from ipray4u import limiter
from ipray4u.utils.success_messages import get_success
from ipray4u.routes.auth import PASSWORD_RESET_TOKEN_HASH_KEY
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


def test_login_with_invalid_credentials_redirects_to_login_and_does_not_set_session(
    client, 
    auth_form_data,
    mock_supabase,
    mocker,
    ):
    
    class FakeAuthApiError(Exception):
        pass
    
    mocker.patch("ipray4u.routes.auth.AuthApiError", FakeAuthApiError)
    
    mock_supabase.auth.sign_in_with_password.side_effect = FakeAuthApiError()
    
    response = client.post(LOGIN_URL, data=auth_form_data)
    
    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL
    
    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session

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


def test_reset_password_page_loads(client):
    response = client.get(RESET_PASSWORD_URL)

    assert response.status_code == 200
    assert b"Reset Password" in response.data
    assert response.data.count(
        b'data-password-toggle="password confirm-password"'
    ) == 2
    assert b">Show<" not in response.data


def test_forgot_password_sends_reset_email(client, mock_supabase):
    response = client.post(
        FORGOT_PASSWORD_URL,
        data={"email": "  person@example.com  "},
    )

    assert response.status_code == 302
    assert response.headers["Location"] == FORGOT_PASSWORD_URL
    mock_supabase.auth.reset_password_for_email.assert_called_once_with(
        "person@example.com",
        {"redirect_to": "https://test.ipray4u.example/reset-password"},
    )


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
    assert b"If an account exists for that email" in missing_account_response.data
    assert b"missing@example.com" not in missing_account_response.data
    assert b"User not found" not in missing_account_response.data


def test_forgot_password_is_rate_limited(client, mock_supabase):
    limiter.reset()

    try:
        responses = [
            client.post(
                FORGOT_PASSWORD_URL,
                data={"email": "person@example.com"},
            )
            for _ in range(6)
        ]
    finally:
        limiter.reset()

    assert all(response.status_code == 302 for response in responses[:5])
    assert responses[5].status_code == 429


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
    assert b"Unable to reset your password" in response.data


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
    )

    assert response.status_code == 400
    assert b"reset link is invalid or expired" in response.data
    mock_supabase.auth.verify_otp.assert_not_called()
    mock_supabase.auth.update_user.assert_not_called()


def test_reset_password_too_short_does_not_update_user(client, mock_supabase):
    response = client.post(
        RESET_PASSWORD_URL,
        data={"password": "short", "confirm-password": "short"},
    )

    assert response.status_code == 400
    assert b"Password must be at least 8 characters" in response.data
    mock_supabase.auth.verify_otp.assert_not_called()
    mock_supabase.auth.update_user.assert_not_called()


def test_reset_password_mismatch_does_not_update_user(client, mock_supabase):
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
    )

    assert response.status_code == 400
    assert b"Unable to reset your password" in response.data
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
    )

    assert response.status_code == 400
    assert b"Unable to reset your password" in response.data
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
