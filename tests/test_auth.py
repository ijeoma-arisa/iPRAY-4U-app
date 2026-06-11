from .helpers.assertions import assert_success_response
from ipray4u.utils.success_messages import get_success
from .helpers.fixtures import client, auth_client
from .helpers.urls import (
    LOGIN_URL,
    LOGOUT_URL, 
    PRAYER_REQUESTS_URL,
)
# Signup Tests
# def test_signup_page_loads(client):
    # Act: GET the signup page

    # Assert: status code is 200
    # Assert: response contains expected signup page text


# def test_signup_with_valid_data_redirects_to_verify_page(client, mocker):
    # Arrange:
    # - mock Supabase sign_up response
    # - prepare valid form data: email, password, maybe display_name

    # Act: POST signup form data to signup route

    # Assert: status code is 302
    # Assert: redirects to verify page
    # Assert: Supabase sign_up was called with expected data


# def test_signup_with_invalid_data_shows_error(client):
    # Arrange:
    # - prepare missing/invalid form data

    # Act: POST signup form

    # Assert: response does not create account
    # Assert: status code is 200 or 400 depending on your design
    # Assert: error message appears


# def test_signup_when_supabase_returns_error_shows_flash_message(client, mocker):
    # Arrange:
    # - mock Supabase sign_up to raise AuthApiError or return failure

    # Act: POST valid-looking signup data

    # Assert: user stays on signup page or is redirected appropriately
    # Assert: error flash/message appears
    
# Verify Tests
# def test_verify_page_loads(client):
    # Act: GET verify page

    # Assert: status code is 200
    # Assert: response contains expected verify-email message


# def test_verify_page_is_reachable_after_signup(client, mocker):
    # Arrange:
    # - mock successful signup

    # Act:
    # - POST signup form

    # Assert:
    # - response redirects to verify page
    
# Login Tests
# def test_login_page_loads(client):
    # Act: GET login page

    # Assert: status code is 200
    # Assert: response contains expected login page text


# def test_login_with_valid_credentials_sets_session_and_redirects(client, mocker):
    # Arrange:
    # - mock Supabase sign_in_with_password response
    # - response should include fake user id and email
    # - prepare valid email/password form data

    # Act: POST login form

    # Assert: status code is 302
    # Assert: redirects to protected page or intended page
    # Assert: session contains user_id
    # Assert: session contains email, if your app stores it


# def test_login_with_invalid_credentials_shows_error(client, mocker):
    # Arrange:
    # - mock Supabase sign_in_with_password to raise auth error

    # Act: POST login form

    # Assert: status code is 200 or redirect, depending on your design
    # Assert: session does not contain user_id
    # Assert: error message appears


# def test_login_with_missing_fields_shows_error(client):
    # Arrange:
    # - missing email or password

    # Act: POST login form

    # Assert: session does not contain user_id
    # Assert: error message appears
    
# Logout Tests
def test_logout_clears_session_and__redirects_to_login(auth_client):
    auth_client.post(LOGOUT_URL)
    
    with auth_client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session
        
    response = auth_client.get(PRAYER_REQUESTS_URL)

    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL


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
    
# CSRF Tests
# def test_logout_without_csrf_token_is_rejected(client_with_csrf_enabled):
    # Arrange:
    # - place user_id in session

    # Act:
    # - POST logout route without csrf_token

    # Assert:
    # - status code is 400
    # - session still contains user_id


# def test_login_without_csrf_token_is_rejected(client_with_csrf_enabled):
    # Act:
    # - POST login form data without csrf_token

    # Assert:
    # - status code is 400


# def test_signup_without_csrf_token_is_rejected(client_with_csrf_enabled):
    # Act:
    # - POST signup form data without csrf_token

    # Assert:
    # - status code is 400