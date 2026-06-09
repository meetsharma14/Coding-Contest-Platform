import sys
import os

# Ensure the backend package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from database import Base, get_db
from main import app
from auth import hash_password
from models import User


# ------------------------------------
# In-memory SQLite for tests
# ------------------------------------

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """Provide a clean DB session for helper operations inside tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client():
    return TestClient(app)


@pytest.fixture()
def participant_user(db):
    """Create a participant user and return (user, raw_password)."""
    raw_password = "testpass123"
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password(raw_password),
        role="participant",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, raw_password


@pytest.fixture()
def admin_user(db):
    """Create an admin user and return (user, raw_password)."""
    raw_password = "adminpass123"
    user = User(
        username="adminuser",
        email="admin@example.com",
        password_hash=hash_password(raw_password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, raw_password


@pytest.fixture()
def creator_user(db):
    """Create a creator user and return (user, raw_password)."""
    raw_password = "creatorpass1"
    user = User(
        username="creatoruser",
        email="creator@example.com",
        password_hash=hash_password(raw_password),
        role="creator",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, raw_password


def auth_header(client, username: str, password: str) -> dict:
    """Login and return Authorization header dict."""
    resp = client.post(
        "/users/login",
        json={"username": username, "password": password},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
