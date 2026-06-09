from tests.conftest import auth_header


class TestUserRegistration:

    def test_register_success(self, client):
        resp = client.post(
            "/users/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        assert data["role"] == "participant"
        assert "id" in data

    def test_register_duplicate_username(self, client, participant_user):
        user, _ = participant_user
        resp = client.post(
            "/users/register",
            json={
                "username": user.username,
                "email": "other@example.com",
                "password": "password123",
            },
        )
        assert resp.status_code == 400
        assert "Username already exists" in resp.json()["detail"]

    def test_register_duplicate_email(self, client, participant_user):
        user, _ = participant_user
        resp = client.post(
            "/users/register",
            json={
                "username": "anotheruser",
                "email": user.email,
                "password": "password123",
            },
        )
        assert resp.status_code == 400
        assert "Email already exists" in resp.json()["detail"]

    def test_register_short_password(self, client):
        resp = client.post(
            "/users/register",
            json={
                "username": "shortpw",
                "email": "short@example.com",
                "password": "short",
            },
        )
        assert resp.status_code == 400

    def test_register_invalid_email(self, client):
        resp = client.post(
            "/users/register",
            json={
                "username": "bademail",
                "email": "not-an-email",
                "password": "password123",
            },
        )
        assert resp.status_code == 422  # Pydantic validation error


class TestUserLogin:

    def test_login_success(self, client, participant_user):
        user, password = participant_user
        resp = client.post(
            "/users/login",
            json={"username": user.username, "password": password},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client, participant_user):
        user, _ = participant_user
        resp = client.post(
            "/users/login",
            json={"username": user.username, "password": "wrongpassword"},
        )
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post(
            "/users/login",
            json={"username": "ghost", "password": "password123"},
        )
        assert resp.status_code == 401


class TestUserProfile:

    def test_get_profile(self, client, participant_user):
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.get("/users/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["username"] == user.username

    def test_get_profile_no_auth(self, client):
        resp = client.get("/users/me")
        assert resp.status_code == 401

    def test_get_profile_invalid_token(self, client):
        resp = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalidtoken"},
        )
        assert resp.status_code == 401
