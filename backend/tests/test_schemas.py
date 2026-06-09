import pytest
from pydantic import ValidationError
from datetime import datetime

from schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenData,
    ProblemCreate,
    ProblemResponse,
    ContestCreate,
    ContestResponse,
    SubmissionCreate,
    SubmissionResponse,
)


class TestUserCreate:

    def test_valid(self):
        u = UserCreate(
            username="alice",
            email="alice@example.com",
            password="secret",
        )
        assert u.username == "alice"
        assert u.email == "alice@example.com"

    def test_invalid_email(self):
        with pytest.raises(ValidationError):
            UserCreate(
                username="alice",
                email="not-an-email",
                password="secret",
            )

    def test_missing_field(self):
        with pytest.raises(ValidationError):
            UserCreate(username="alice", email="a@b.com")


class TestUserLogin:

    def test_valid(self):
        u = UserLogin(username="bob", password="pass")
        assert u.username == "bob"


class TestUserResponse:

    def test_valid(self):
        now = datetime.utcnow()
        u = UserResponse(
            id=1,
            username="alice",
            email="alice@example.com",
            role="participant",
            created_at=now,
        )
        assert u.id == 1


class TestToken:

    def test_valid(self):
        t = Token(access_token="abc", token_type="bearer")
        assert t.access_token == "abc"


class TestTokenData:

    def test_optional_username(self):
        t = TokenData()
        assert t.username is None

    def test_with_username(self):
        t = TokenData(username="alice")
        assert t.username == "alice"


class TestProblemCreate:

    def test_valid_minimal(self):
        p = ProblemCreate(
            title="Two Sum",
            difficulty="Easy",
            description="Add two numbers",
        )
        assert p.sample_input is None

    def test_valid_full(self):
        p = ProblemCreate(
            title="Two Sum",
            difficulty="Easy",
            description="Add two numbers",
            sample_input="1 2",
            sample_output="3",
        )
        assert p.sample_output == "3"


class TestProblemResponse:

    def test_valid(self):
        p = ProblemResponse(
            id=1,
            title="Two Sum",
            difficulty="Easy",
            description="Add two numbers",
        )
        assert p.id == 1


class TestContestCreate:

    def test_valid(self):
        c = ContestCreate(
            title="Weekly 1",
            description="First weekly",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
        )
        assert c.title == "Weekly 1"

    def test_missing_times(self):
        with pytest.raises(ValidationError):
            ContestCreate(title="X", description="Y")


class TestContestResponse:

    def test_valid(self):
        c = ContestResponse(
            id=1,
            title="Weekly 1",
            description="First weekly",
            start_time=datetime(2025, 1, 1, 10, 0),
            end_time=datetime(2025, 1, 1, 12, 0),
            is_active=False,
        )
        assert c.is_active is False


class TestSubmissionCreate:

    def test_defaults(self):
        s = SubmissionCreate(problem_id=1, code="print('hi')")
        assert s.language == "python"

    def test_custom_language(self):
        s = SubmissionCreate(problem_id=1, code="x", language="cpp")
        assert s.language == "cpp"


class TestSubmissionResponse:

    def test_valid(self):
        now = datetime.utcnow()
        s = SubmissionResponse(
            id=1,
            user_id=1,
            problem_id=1,
            verdict="Accepted",
            score=100,
            runtime_ms=5,
            submitted_at=now,
        )
        assert s.verdict == "Accepted"
