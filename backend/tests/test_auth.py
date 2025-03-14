import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from jose import JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.services.auth import AuthService
from app.models.user import User
from app.core.config import settings
from app.core.security import create_access_token

@pytest.fixture
def mock_db():
    return Mock(spec=Session)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password",
        full_name="Test User"
    )

@pytest.fixture
def auth_service(mock_db):
    return AuthService(mock_db)

def test_create_user(auth_service):
    # Arrange
    username = "newuser"
    email = "new@example.com"
    password = "testpass123"
    full_name = "New User"
    auth_service.db.add = Mock()
    auth_service.db.commit = Mock()
    auth_service.db.refresh = Mock()

    # Act
    user = auth_service.create_user(
        username=username,
        email=email,
        password=password,
        full_name=full_name
    )

    # Assert
    assert user.username == username
    assert user.email == email
    assert user.full_name == full_name
    assert user.hashed_password != password  # Password should be hashed
    auth_service.db.add.assert_called_once()
    auth_service.db.commit.assert_called_once()
    auth_service.db.refresh.assert_called_once()

def test_get_user_by_username(auth_service, mock_user):
    # Arrange
    auth_service.db.query.return_value.filter.return_value.first.return_value = mock_user

    # Act
    user = auth_service.get_user_by_username(mock_user.username)

    # Assert
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    assert user.email == mock_user.email
    auth_service.db.query.assert_called_once_with(User)

def test_get_user_by_username_not_found(auth_service):
    # Arrange
    auth_service.db.query.return_value.filter.return_value.first.return_value = None

    # Act
    user = auth_service.get_user_by_username("nonexistent")

    # Assert
    assert user is None

def test_authenticate_user(auth_service, mock_user):
    # Arrange
    auth_service.get_user_by_username = Mock(return_value=mock_user)
    auth_service.verify_password = Mock(return_value=True)

    # Act
    user = auth_service.authenticate_user("testuser", "testpass")

    # Assert
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    auth_service.get_user_by_username.assert_called_once_with("testuser")
    auth_service.verify_password.assert_called_once()

def test_authenticate_user_invalid_credentials(auth_service, mock_user):
    # Arrange
    auth_service.get_user_by_username = Mock(return_value=mock_user)
    auth_service.verify_password = Mock(return_value=False)

    # Act
    user = auth_service.authenticate_user("testuser", "wrongpass")

    # Assert
    assert user is None

def test_authenticate_user_not_found(auth_service):
    # Arrange
    auth_service.get_user_by_username = Mock(return_value=None)

    # Act
    user = auth_service.authenticate_user("nonexistent", "testpass")

    # Assert
    assert user is None

def test_verify_password(auth_service):
    # Arrange
    password = "testpass123"
    hashed_password = auth_service.get_password_hash(password)

    # Act
    is_valid = auth_service.verify_password(password, hashed_password)

    # Assert
    assert is_valid is True

def test_verify_password_invalid(auth_service):
    # Arrange
    password = "testpass123"
    hashed_password = auth_service.get_password_hash(password)

    # Act
    is_valid = auth_service.verify_password("wrongpass", hashed_password)

    # Assert
    assert is_valid is False

def test_get_password_hash(auth_service):
    # Arrange
    password = "testpass123"

    # Act
    hashed_password = auth_service.get_password_hash(password)

    # Assert
    assert hashed_password != password
    assert isinstance(hashed_password, str)

def test_create_access_token():
    # Arrange
    data = {"sub": "testuser"}
    expires_delta = timedelta(minutes=15)

    # Act
    token = create_access_token(data, expires_delta)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_no_expiry():
    # Arrange
    data = {"sub": "testuser"}

    # Act
    token = create_access_token(data)

    # Assert
    assert isinstance(token, str)
    assert len(token) > 0

def test_get_current_user(auth_service, mock_user):
    # Arrange
    token = create_access_token({"sub": mock_user.username})
    auth_service.get_user_by_username = Mock(return_value=mock_user)

    # Act
    user = auth_service.get_current_user(token)

    # Assert
    assert user.id == mock_user.id
    assert user.username == mock_user.username
    auth_service.get_user_by_username.assert_called_once_with(mock_user.username)

def test_get_current_user_invalid_token(auth_service):
    # Arrange
    token = "invalid.token.string"

    # Act & Assert
    with pytest.raises(JWTError):
        auth_service.get_current_user(token)

def test_get_current_user_user_not_found(auth_service):
    # Arrange
    token = create_access_token({"sub": "nonexistent"})
    auth_service.get_user_by_username = Mock(return_value=None)

    # Act & Assert
    with pytest.raises(ValueError) as exc_info:
        auth_service.get_current_user(token)
    assert str(exc_info.value) == "User not found" 