import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import jwt
from Backend.utils.auth import AuthService
from Backend.database.database import init_db

# Test configurations
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "ai_ocr_test_db"
JWT_SECRET_KEY = "your-test-secret-key"
ALGORITHM = "HS256"

@pytest.fixture
async def test_app():
    """Create a test instance of the application"""
    from Backend.main import app
    
    # Override MongoDB settings for testing
    app.mongodb_client = AsyncIOMotorClient(TEST_MONGODB_URL)
    app.mongodb = app.mongodb_client[TEST_DB_NAME]
    
    # Initialize test database
    await init_db(app.mongodb)
    
    yield app
    
    # Cleanup after tests
    await app.mongodb.client.drop_database(TEST_DB_NAME)

@pytest.fixture
async def test_client(test_app):
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client

@pytest.mark.asyncio
async def test_register_user(test_client):
    """Test user registration endpoint"""
    response = await test_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "User created successfully"

@pytest.mark.asyncio
async def test_login_user(test_client):
    """Test user login endpoint"""
    # First register a user
    await test_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Then try to login
    response = await test_client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_get_current_user(test_client):
    """Test get current user endpoint"""
    # Register and login first
    await test_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    login_response = await test_client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Then get current user info
    response = await test_client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_invalid_login(test_client):
    """Test login with invalid credentials"""
    response = await test_client.post(
        "/auth/token",
        data={
            "username": "nonexistent@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401