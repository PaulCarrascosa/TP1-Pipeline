"""API tests"""
import pytest
from src.models.users import User
from src.utils.security import get_password_hash


@pytest.fixture
def user_client(client, db_session):
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Test User",
        is_active=True,
        is_admin=False
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "user@test.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest.fixture
def admin_client(client, db_session):
    user = User(
        email="admin@test.com",
        hashed_password=get_password_hash("password123"),
        full_name="Admin User",
        is_active=True,
        is_admin=True
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin@test.com", "password": "password123"}
    )
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_list_books(user_client):
    response = user_client.get("/api/v1/books/")
    assert response.status_code == 200


def test_list_users(admin_client):
    response = admin_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_loans(admin_client):
    response = admin_client.get("/api/v1/loans/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
