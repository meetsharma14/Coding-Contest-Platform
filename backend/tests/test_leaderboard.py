from unittest.mock import patch

from tests.conftest import auth_header
from models import Problem, Submission


def _seed_problem(db):
    problem = Problem(
        id=1,
        title="P1",
        difficulty="Easy",
        description="Desc",
    )
    db.add(problem)
    db.commit()
    db.refresh(problem)
    return problem


ACCEPTED_RESULT = {
    "verdict": "Accepted",
    "score": 100,
    "runtime_ms": 5,
}


class TestGlobalLeaderboard:

    def test_empty(self, client):
        resp = client.get("/leaderboard/")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_users_no_submissions(self, client, participant_user):
        resp = client.get("/leaderboard/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["rank"] == 1
        assert data[0]["total_score"] == 0

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_with_submissions(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "x=1"},
            headers=headers,
        )
        resp = client.get("/leaderboard/")
        assert resp.status_code == 200
        data = resp.json()
        assert data[0]["total_score"] == 100
        assert data[0]["accepted"] == 1


class TestTop10:

    def test_empty(self, client):
        resp = client.get("/leaderboard/top10")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_with_users_raises_due_to_row_serialization(self, client, participant_user):
        """top_10_users returns raw SQLAlchemy Row objects that FastAPI cannot
        serialise to JSON.  This test documents the existing bug; the endpoint
        needs a response_model or manual dict conversion to work."""
        import pytest
        with pytest.raises(ValueError):
            client.get("/leaderboard/top10")


class TestUserStats:

    def test_existing_user_no_submissions(self, client, participant_user):
        user, _ = participant_user
        resp = client.get(f"/leaderboard/user/{user.id}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == user.username
        assert data["total_score"] == 0

    def test_nonexistent_user(self, client):
        resp = client.get("/leaderboard/user/999")
        assert resp.status_code == 200
        assert resp.json()["error"] == "User not found"

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_user_with_submissions(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "x=1"},
            headers=headers,
        )
        resp = client.get(f"/leaderboard/user/{user.id}")
        data = resp.json()
        assert data["total_score"] == 100
        assert data["total_submissions"] == 1
        assert data["accepted"] == 1
