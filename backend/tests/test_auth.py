import pytest
from datetime import timedelta
from jose import jwt
from fastapi import HTTPException

from auth import (
    hash_password,
    verify_password,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)


class TestHashPassword:

    def test_returns_hashed_string(self):
        hashed = hash_password("longpassword")
        assert hashed != "longpassword"
        assert len(hashed) > 0

    def test_short_password_raises(self):
        with pytest.raises(HTTPException) as exc_info:
            hash_password("short")
        assert exc_info.value.status_code == 400
        assert "8 characters" in exc_info.value.detail

    def test_exactly_8_chars_ok(self):
        hashed = hash_password("12345678")
        assert hashed is not None

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("samepassword")
        h2 = hash_password("samepassword")
        assert h1 != h2  # salted hashes differ


class TestVerifyPassword:

    def test_correct_password(self):
        hashed = hash_password("mypassword1")
        assert verify_password("mypassword1", hashed) is True

    def test_wrong_password(self):
        hashed = hash_password("mypassword1")
        assert verify_password("wrongpassword", hashed) is False


class TestCreateAccessToken:

    def test_token_contains_subject(self):
        token = create_access_token(data={"sub": "alice"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "alice"

    def test_token_contains_expiry(self):
        token = create_access_token(data={"sub": "bob"})
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert "exp" in payload

    def test_custom_expiry(self):
        token = create_access_token(
            data={"sub": "charlie"},
            expires_delta=timedelta(minutes=5),
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "charlie"

    def test_default_expiry_uses_config(self):
        assert ACCESS_TOKEN_EXPIRE_MINUTES == 60
