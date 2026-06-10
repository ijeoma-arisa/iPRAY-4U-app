from .helpers.fixtures import client, auth_client
from .helpers.urls import LOGOUT_URL, PRAYER_REQUESTS_URL

def test_logout_clears_session_and_protects_page(auth_client):
    auth_client.post(LOGOUT_URL)
    
    with auth_client.session_transaction() as session:
        assert "user_id" not in session
        assert "email" not in session
        
    response = auth_client.get(PRAYER_REQUESTS_URL)
    
    assert response.status_code == 302
 
    
    