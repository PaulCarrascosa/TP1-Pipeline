import pytest
from sqlalchemy.orm import Session

from src.models.users import User
from src.repositories.users import UserRepository
from src.services.users import UserService
from src.api.schemas.users import UserCreate, UserUpdate


def test_create_user(db_session: Session):
    repository = UserRepository(User, db_session)
    service = UserService(repository)

    user_in = UserCreate(
        email="test@example.com",
        password="password123",
        full_name="Test User",
        is_active=True,
        is_admin=False
    )

    user = service.create(obj_in=user_in)

    assert user.email == "test@example.com"
    assert user.full_name == "Test User"
    assert user.is_active is True
    assert user.is_admin is False
    assert hasattr(user, "hashed_password")
    assert user.hashed_password != "password123"


def test_authenticate_user(db_session: Session):
    repository = UserRepository(User, db_session)
    service = UserService(repository)

    user_in = UserCreate(
        email="auth@example.com",
        password="password123",
        full_name="Auth User"
    )

    user = service.create(obj_in=user_in)

    authenticated_user = service.authenticate(email="auth@example.com", password="password123")
    assert authenticated_user is not None
    assert authenticated_user.id == user.id

    authenticated_user = service.authenticate(email="auth@example.com", password="wrongpassword")
    assert authenticated_user is None

    authenticated_user = service.authenticate(email="nonexistent@example.com", password="password123")
    assert authenticated_user is None


def test_update_user(db_session: Session):
    repository = UserRepository(User, db_session)
    service = UserService(repository)

    user_in = UserCreate(
        email="update@example.com",
        password="password123",
        full_name="Update User"
    )

    user = service.create(obj_in=user_in)
    old_hash = user.hashed_password

    user_update = UserUpdate(full_name="Updated Name")
    updated_user = service.update(db_obj=user, obj_in=user_update)

    assert updated_user.id == user.id
    assert updated_user.full_name == "Updated Name"
    assert updated_user.hashed_password == old_hash

    user_update = UserUpdate(password="newpassword123")
    updated_user = service.update(db_obj=updated_user, obj_in=user_update)

    assert updated_user.hashed_password != old_hash

    authenticated_user = service.authenticate(email="update@example.com", password="newpassword123")
    assert authenticated_user is not None
    assert authenticated_user.id == user.id


def test_get_by_email(db_session: Session):
    repository = UserRepository(User, db_session)
    service = UserService(repository)

    user_in = UserCreate(
        email="get@example.com",
        password="password123",
        full_name="Get User"
    )

    user = service.create(obj_in=user_in)

    retrieved_user = service.get_by_email(email="get@example.com")
    assert retrieved_user is not None
    assert retrieved_user.id == user.id

    retrieved_user = service.get_by_email(email="nonexistent@example.com")
    assert retrieved_user is None


def test_create_user_email_already_used(db_session: Session):
    repository = UserRepository(User, db_session)
    service = UserService(repository)

    user_in = UserCreate(
        email="duplicate@example.com",
        password="password123",
        full_name="Duplicate User"
    )

    service.create(obj_in=user_in)

    with pytest.raises(ValueError):
        service.create(obj_in=user_in)
