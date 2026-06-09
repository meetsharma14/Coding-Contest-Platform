"""Tests for the submissions router.

NOTE: The router calls ``run_python_code(submission.code, test_cases)``
but the ``judge.run_python_code`` function only accepts a single positional
argument (``code``).  The tests below therefore patch ``judge.run_python_code``
inside the router module so the endpoint can be exercised without hitting
that signature mismatch.
"""

from unittest.mock import patch

from tests.conftest import auth_header
from models import Problem


def _seed_problem(db):
    """Insert a problem directly so it's available for submissions."""
    problem = Problem(
        id=1,
        title="Two Sum",
        difficulty="Easy",
        description="Return sum",
        sample_input="1 2",
        sample_output="3",
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


class TestSubmitSolution:

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_submit_success(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "print(1+2)", "language": "python"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "Accepted"
        assert data["score"] == 100

    def test_submit_no_auth(self, client):
        resp = client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "x=1"},
        )
        assert resp.status_code == 401

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_submit_problem_not_found(self, mock_judge, client, participant_user):
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.post(
            "/submissions/",
            json={"problem_id": 999, "code": "x=1"},
            headers=headers,
        )
        assert resp.status_code == 404

    @patch(
        "routers.submissions.run_python_code",
        return_value={
            "verdict": "Compilation Error",
            "score": 0,
            "runtime_ms": 0,
            "error": "syntax error",
        },
    )
    def test_submit_compilation_error(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "def foo("},
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["verdict"] == "Compilation Error"
        assert resp.json()["score"] == 0


class TestMySubmissions:

    def test_no_auth(self, client):
        resp = client.get("/submissions/my")
        assert resp.status_code == 401

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_returns_user_submissions(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        # Submit twice
        client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "a=1"},
            headers=headers,
        )
        client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "a=2"},
            headers=headers,
        )
        resp = client.get("/submissions/my", headers=headers)
        assert resp.status_code == 200
        assert len(resp.json()) == 2


class TestGetSubmission:

    @patch(
        "routers.submissions.run_python_code",
        return_value=ACCEPTED_RESULT,
    )
    def test_get_existing(self, mock_judge, client, participant_user, db):
        _seed_problem(db)
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        create_resp = client.post(
            "/submissions/",
            json={"problem_id": 1, "code": "x=1"},
            headers=headers,
        )
        sid = create_resp.json()["id"]
        resp = client.get(f"/submissions/{sid}", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["id"] == sid

    def test_get_nonexistent(self, client, participant_user):
        user, password = participant_user
        headers = auth_header(client, user.username, password)
        resp = client.get("/submissions/999", headers=headers)
        assert resp.status_code == 404
