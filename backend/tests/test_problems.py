import pytest
from tests.conftest import auth_header
from models import Problem


def _create_problem(client):
    """Helper: create a problem via API."""
    return client.post(
        "/problems/",
        json={
            "title": "Two Sum",
            "difficulty": "Easy",
            "description": "Return sum of two numbers",
            "sample_input": "1 2",
            "sample_output": "3",
        },
    )


class TestCreateProblem:

    def test_create_success(self, client):
        resp = _create_problem(client)
        assert resp.status_code == 201
        data = resp.json()
        assert data["title"] == "Two Sum"
        assert data["difficulty"] == "Easy"
        assert "id" in data

    def test_create_duplicate_title(self, client):
        _create_problem(client)
        resp = _create_problem(client)
        assert resp.status_code == 400
        assert "Problem already exists" in resp.json()["detail"]

    def test_create_minimal_fields(self, client):
        resp = client.post(
            "/problems/",
            json={
                "title": "Minimal",
                "difficulty": "Hard",
                "description": "A hard problem",
            },
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["sample_input"] is None


class TestGetProblems:

    def test_get_all_empty(self, client):
        resp = client.get("/problems/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_all_with_data(self, client):
        _create_problem(client)
        resp = client.get("/problems/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1

    def test_filter_by_difficulty(self, client):
        _create_problem(client)
        client.post(
            "/problems/",
            json={
                "title": "Hard One",
                "difficulty": "Hard",
                "description": "Very hard",
            },
        )
        resp = client.get("/problems/?difficulty=Easy")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
        assert resp.json()[0]["difficulty"] == "Easy"

    def test_filter_no_match(self, client):
        _create_problem(client)
        resp = client.get("/problems/?difficulty=Medium")
        assert resp.status_code == 200
        assert len(resp.json()) == 0


class TestGetSingleProblem:

    def test_get_existing(self, client):
        create_resp = _create_problem(client)
        pid = create_resp.json()["id"]
        resp = client.get(f"/problems/{pid}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Two Sum"

    def test_get_nonexistent(self, client):
        resp = client.get("/problems/999")
        assert resp.status_code == 404


class TestDeleteProblem:

    def test_delete_as_admin(self, client, admin_user):
        create_resp = _create_problem(client)
        pid = create_resp.json()["id"]
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        resp = client.delete(f"/problems/{pid}", headers=headers)
        assert resp.status_code == 200
        assert "deleted" in resp.json()["message"].lower()

    def test_delete_nonexistent(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        resp = client.delete("/problems/999", headers=headers)
        assert resp.status_code == 404

    def test_delete_as_participant_forbidden(self, client, participant_user):
        create_resp = _create_problem(client)
        pid = create_resp.json()["id"]
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.delete(f"/problems/{pid}", headers=headers)
        assert resp.status_code == 403

    def test_delete_no_auth(self, client):
        create_resp = _create_problem(client)
        pid = create_resp.json()["id"]
        resp = client.delete(f"/problems/{pid}")
        assert resp.status_code == 401
