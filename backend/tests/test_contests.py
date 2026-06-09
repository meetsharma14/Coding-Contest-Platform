from tests.conftest import auth_header


def _create_contest(client, headers, title="Weekly 1"):
    """Helper: create a contest via API (admin required)."""
    return client.post(
        "/contests/",
        json={
            "title": title,
            "description": "A weekly contest",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T12:00:00",
        },
        headers=headers,
    )


class TestCreateContest:

    def test_create_success(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        resp = _create_contest(client, headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Weekly 1"
        assert data["is_active"] is False

    def test_create_as_participant_forbidden(self, client, participant_user):
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = _create_contest(client, headers)
        assert resp.status_code == 403

    def test_create_no_auth(self, client):
        resp = client.post(
            "/contests/",
            json={
                "title": "X",
                "description": "Y",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T12:00:00",
            },
        )
        assert resp.status_code == 401


class TestGetContests:

    def test_get_all_empty(self, client):
        resp = client.get("/contests/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_all_with_data(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        _create_contest(client, headers)
        resp = client.get("/contests/")
        assert resp.status_code == 200
        assert len(resp.json()) == 1


class TestGetContestById:

    def test_existing(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        create_resp = _create_contest(client, headers)
        cid = create_resp.json()["id"]
        resp = client.get(f"/contests/{cid}")
        assert resp.status_code == 200
        assert resp.json()["title"] == "Weekly 1"

    def test_nonexistent(self, client):
        resp = client.get("/contests/999")
        assert resp.status_code == 404


class TestAddProblemToContest:

    def test_add_problem_success(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        # Create contest
        contest_resp = _create_contest(client, headers)
        cid = contest_resp.json()["id"]
        # Create problem
        prob_resp = client.post(
            "/problems/",
            json={
                "title": "P1",
                "difficulty": "Easy",
                "description": "Desc",
            },
        )
        pid = prob_resp.json()["id"]
        resp = client.post(
            f"/contests/{cid}/add-problem/{pid}", headers=headers
        )
        assert resp.status_code == 200
        assert "added" in resp.json()["message"].lower()

    def test_add_problem_contest_not_found(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        prob_resp = client.post(
            "/problems/",
            json={
                "title": "P2",
                "difficulty": "Easy",
                "description": "Desc",
            },
        )
        pid = prob_resp.json()["id"]
        resp = client.post(
            f"/contests/999/add-problem/{pid}", headers=headers
        )
        assert resp.status_code == 404

    def test_add_problem_problem_not_found(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        contest_resp = _create_contest(client, headers)
        cid = contest_resp.json()["id"]
        resp = client.post(
            f"/contests/{cid}/add-problem/999", headers=headers
        )
        assert resp.status_code == 404


class TestStartEndContest:

    def test_start_contest(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        contest_resp = _create_contest(client, headers)
        cid = contest_resp.json()["id"]
        resp = client.put(f"/contests/{cid}/start", headers=headers)
        assert resp.status_code == 200
        assert "started" in resp.json()["message"].lower()

    def test_end_contest(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        contest_resp = _create_contest(client, headers)
        cid = contest_resp.json()["id"]
        # Start then end
        client.put(f"/contests/{cid}/start", headers=headers)
        resp = client.put(f"/contests/{cid}/end", headers=headers)
        assert resp.status_code == 200
        assert "ended" in resp.json()["message"].lower()

    def test_start_nonexistent(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        resp = client.put("/contests/999/start", headers=headers)
        assert resp.status_code == 404

    def test_end_nonexistent(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        resp = client.put("/contests/999/end", headers=headers)
        assert resp.status_code == 404

    def test_start_as_participant_forbidden(self, client, admin_user, participant_user):
        admin, admin_pw = admin_user
        admin_headers = auth_header(client, admin.username, admin_pw)
        contest_resp = _create_contest(client, admin_headers)
        cid = contest_resp.json()["id"]
        user, user_pw = participant_user
        user_headers = auth_header(client, user.username, user_pw)
        resp = client.put(f"/contests/{cid}/start", headers=user_headers)
        assert resp.status_code == 403


class TestActiveContests:

    def test_no_active(self, client):
        resp = client.get("/contests/active/list")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_active_after_start(self, client, admin_user):
        admin, password = admin_user
        headers = auth_header(client, admin.username, password)
        contest_resp = _create_contest(client, headers)
        cid = contest_resp.json()["id"]
        client.put(f"/contests/{cid}/start", headers=headers)
        resp = client.get("/contests/active/list")
        assert resp.status_code == 200
        assert len(resp.json()) == 1
