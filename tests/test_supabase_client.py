from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from types import SimpleNamespace

import httpx
from supabase_auth import SyncGoTrueClient

from ipray4u.routes.auth import PASSWORD_RESET_TOKEN_HASH_KEY
from ipray4u.supabase_client import get_supabase
from .helpers.urls import LOGIN_URL, RESET_PASSWORD_URL


class FakeAuth:
    def __init__(self, client):
        self.client = client
        self.session = None

    def sign_in_with_password(self, credentials):
        if credentials.get("email") == "rejected@example.com":
            self.session = None
            raise AuthenticationRejectedError()

        self.session = object()
        self.client.options.headers["Authorization"] = "Bearer request-session"
        return SimpleNamespace(
            user=SimpleNamespace(id="user-id", email=credentials["email"]),
            session=self.session,
        )

    def sign_up(self, credentials):
        self.session = object()
        self.client.options.headers["Authorization"] = "Bearer signup-session"
        return SimpleNamespace(user=object(), session=self.session)

    def verify_otp(self, params):
        self.session = object()
        self.client.verified_session = self.session
        return SimpleNamespace(session=self.session, user=object())

    def update_user(self, attributes):
        assert self.session is self.client.verified_session
        self.client.updated_with_verified_session = True
        return SimpleNamespace(user=object())

    def sign_out(self, options=None):
        self.session = None


class FakeSupabaseClient:
    def __init__(self):
        self.options = SimpleNamespace(
            headers={"Authorization": "Bearer publishable-key"}
        )
        self.auth = FakeAuth(self)
        self.verified_session = None
        self.updated_with_verified_session = False


class AuthenticationRejectedError(Exception):
    pass


def test_get_supabase_reuses_client_within_request(app, mocker):
    create_client = mocker.patch(
        "ipray4u.supabase_client.create_client",
        return_value=FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()
        second_client = get_supabase()

    assert first_client is second_client
    create_client.assert_called_once()


def test_get_supabase_uses_different_clients_for_separate_requests(app, mocker):
    create_client = mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()

    with app.test_request_context():
        second_client = get_supabase()

    assert first_client is not second_client
    assert create_client.call_count == 2


def test_get_supabase_disables_session_persistence_and_refresh(app, mocker):
    create_client = mocker.patch(
        "ipray4u.supabase_client.create_client",
        return_value=FakeSupabaseClient(),
    )

    with app.test_request_context():
        get_supabase()

    options = create_client.call_args.kwargs["options"]
    assert options.persist_session is False
    assert options.auto_refresh_token is False


def test_pinned_sdk_recovery_session_is_available_to_update_user():
    user = {
        "id": "00000000-0000-0000-0000-000000000001",
        "aud": "authenticated",
        "role": "authenticated",
        "email": "person@example.com",
        "app_metadata": {},
        "user_metadata": {},
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }
    request_paths = []

    def handle_request(request):
        request_paths.append(request.url.path)
        if request.url.path.endswith("/verify"):
            return httpx.Response(
                200,
                json={
                    "access_token": "test-access-token",
                    "refresh_token": "test-refresh-token",
                    "token_type": "bearer",
                    "expires_in": 3600,
                    "user": user,
                },
            )
        if request.url.path.endswith("/user"):
            assert request.headers["Authorization"] == "Bearer test-access-token"
            return httpx.Response(200, json=user)
        raise AssertionError("Unexpected SDK request")

    http_client = httpx.Client(transport=httpx.MockTransport(handle_request))
    auth = SyncGoTrueClient(
        url="https://example.invalid/auth/v1",
        persist_session=False,
        auto_refresh_token=False,
        http_client=http_client,
    )

    recovery_response = auth.verify_otp(
        {"token_hash": "test-recovery-token", "type": "recovery"}
    )
    update_response = auth.update_user({"password": "not-a-real-password"})

    assert recovery_response.session is auth.get_session()
    assert update_response.user.id == recovery_response.user.id
    assert request_paths == ["/auth/v1/verify", "/auth/v1/user"]
    assert auth._refresh_token_timer is None


def test_auth_state_and_authorization_header_do_not_cross_requests(app, mocker):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()
        first_client.auth.sign_in_with_password(
            {"email": "first@example.com", "password": "not-a-real-password"}
        )
        first_session = first_client.auth.session

    with app.test_request_context():
        second_client = get_supabase()

    assert second_client.auth.session is None
    assert second_client.options.headers["Authorization"] == "Bearer publishable-key"
    assert first_client.auth.session is first_session


def test_login_requests_cannot_overwrite_each_others_sdk_sessions(app, mocker):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()
        first_client.auth.sign_in_with_password(
            {"email": "first@example.com", "password": "not-a-real-password"}
        )
        first_session = first_client.auth.session

    with app.test_request_context():
        second_client = get_supabase()
        second_client.auth.sign_in_with_password(
            {"email": "second@example.com", "password": "not-a-real-password"}
        )

    assert first_client.auth.session is first_session
    assert second_client.auth.session is not first_session


def test_failed_login_cannot_clear_another_requests_sdk_session(app, mocker):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()
        first_client.auth.session = object()
        first_session = first_client.auth.session

    with app.test_request_context():
        second_client = get_supabase()
        second_client.auth.session = object()
        try:
            second_client.auth.sign_in_with_password(
                {
                    "email": "rejected@example.com",
                    "password": "not-a-real-password",
                }
            )
        except AuthenticationRejectedError:
            pass
        else:
            raise AssertionError("Controlled failed login unexpectedly succeeded")

    assert first_client.auth.session is first_session
    assert second_client.auth.session is None


def test_signup_cannot_replace_another_requests_sdk_session(app, mocker):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    with app.test_request_context():
        first_client = get_supabase()
        first_client.auth.session = object()
        first_session = first_client.auth.session

    with app.test_request_context():
        signup_client = get_supabase()
        signup_client.auth.sign_up(
            {"email": "new@example.com", "password": "not-a-real-password"}
        )

    assert first_client.auth.session is first_session
    assert signup_client.auth.session is not first_session


def test_password_recovery_verification_and_update_share_request_client(
    client,
    mocker,
):
    recovery_client = FakeSupabaseClient()
    create_client = mocker.patch(
        "ipray4u.supabase_client.create_client",
        return_value=recovery_client,
    )

    with client.session_transaction() as flask_session:
        flask_session[PASSWORD_RESET_TOKEN_HASH_KEY] = "recovery-token"

    response = client.post(
        RESET_PASSWORD_URL,
        data={
            "password": "new-password",
            "confirm-password": "new-password",
        },
    )

    assert response.status_code == 302
    assert response.headers["Location"] == LOGIN_URL
    assert recovery_client.updated_with_verified_session
    create_client.assert_called_once()


def test_concurrent_requests_use_distinct_clients_and_sessions(app, mocker):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )

    contexts_active = Barrier(2)
    sessions_checked = Barrier(2)

    def authenticate(email):
        with app.test_request_context():
            request_client = get_supabase()
            request_client.auth.sign_in_with_password(
                {"email": email, "password": "not-a-real-password"}
            )
            request_session = request_client.auth.session

            contexts_active.wait(timeout=5)
            assert request_client.auth.session is request_session
            sessions_checked.wait(timeout=5)

            return request_client, request_session

    with ThreadPoolExecutor(max_workers=2) as executor:
        first_future = executor.submit(authenticate, "first@example.com")
        second_future = executor.submit(authenticate, "second@example.com")
        first_client, first_session = first_future.result()
        second_client, second_session = second_future.result()

    assert first_client is not second_client
    assert first_session is not second_session
    assert first_client.auth.session is first_session
    assert second_client.auth.session is second_session


def test_existing_login_and_logout_keep_flask_session_behavior(
    client,
    mocker,
):
    mocker.patch(
        "ipray4u.supabase_client.create_client",
        side_effect=lambda *args, **kwargs: FakeSupabaseClient(),
    )
    mocker.patch("ipray4u.routes.auth.ensure_profile_exists")

    login_response = client.post(
        LOGIN_URL,
        data={"email": "person@example.com", "password": "not-a-real-password"},
    )

    assert login_response.status_code == 302
    with client.session_transaction() as flask_session:
        assert flask_session["user_id"] == "user-id"
        assert flask_session["email"] == "person@example.com"

    logout_response = client.post("/logout")

    assert logout_response.status_code == 302
    assert logout_response.headers["Location"] == LOGIN_URL
    with client.session_transaction() as flask_session:
        assert "user_id" not in flask_session
        assert "email" not in flask_session
