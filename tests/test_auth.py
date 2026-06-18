from .helpers.assertions import assert_success_response
from ipray4u.utils.success_messages import get_success
from .helpers.fixtures import (
    app,
    client,
    test_user, 
    auth_client, 
    auth_form_data, 
    mock_supabase, 
    mock_login_response,
)
from .helpers.urls import (
    SIGNUP_URL,
    VERIFY_URL,
    LOGIN_URL,
    LOGOUT_URL, 
    PRAYER_REQUESTS_URL,
)
# Signup Tests
def test_signup_page_loads(client):
    response = client.get(SIGNUP_URL)
    
    assert response.status_code == 200
    assert b"Sign Up" in response.data

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

    
# TODO: Verify Tests
    
# Login Tests
def test_login_page_loads(client):
    response = client.get(LOGIN_URL)
    
    assert response.status_code == 200
    assert b"Log In" in response.data


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
    
# TODO: CSRF Tests