import pytest
from app import create_user, get_user, authenticate_user, delete_user

# Test setup: create a test user dictionary
@pytest.fixture
def new_user():
    return {"username": "testuser", "email": "testuser@example.com", "password": "securepassword123"}

# Test: Create User
def test_create_user(new_user):
    created_user = create_user(new_user)
    assert created_user["username"] == "testuser"
    assert created_user["email"] == "testuser@example.com"
    
# Test: Get User
def test_get_user(new_user):
    create_user(new_user)
    fetched_user = get_user(new_user["username"])
    assert fetched_user["username"] == "testuser"
    assert fetched_user["email"] == "testuser@example.com"

# Test: Prevent Duplicate User Creation
def test_create_duplicate_user(new_user):
    create_user(new_user)
    with pytest.raises(Exception):  # Assuming create_user throws an exception on duplicate
        create_user(new_user)

# Test: Authenticate User with correct credentials
def test_authenticate_user_success(new_user):
    create_user(new_user)
    is_authenticated = authenticate_user(new_user["username"], new_user["password"])
    assert is_authenticated is True

# Test: Authenticate User with incorrect credentials
def test_authenticate_user_failure(new_user):
    create_user(new_user)
    is_authenticated = authenticate_user(new_user["username"], "wrongpassword")
    assert is_authenticated is False

# Test: User Not Found (Authentication)
def test_authenticate_nonexistent_user():
    is_authenticated = authenticate_user("nonexistentuser", "password")
    assert is_authenticated is False

# Test: Delete User
def test_delete_user(new_user):
    create_user(new_user)
    delete_user(new_user["username"])
    with pytest.raises(Exception):  # Assuming get_user throws an exception if user is not found
        get_user(new_user["username"])
