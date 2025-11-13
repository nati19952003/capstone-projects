import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from Backend.main import app
from Backend.database.database import init_db
import os
import json
import cv2
import numpy as np
from pathlib import Path

# Test configurations
TEST_MONGODB_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "ai_ocr_test_db"

@pytest.fixture
async def test_app():
    """Create a test instance of the application"""
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

@pytest.fixture
async def authenticated_client(test_client):
    """Get an authenticated test client"""
    # Register a test user
    await test_client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    
    # Login and get token
    login_response = await test_client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Create a new client with authentication headers
    async with AsyncClient(
        app=test_app,
        base_url="http://test",
        headers={"Authorization": f"Bearer {token}"}
    ) as client:
        yield client

# Sample test image creation
def create_sample_table_image():
    # Create a 500x500 white image
    img = np.ones((500, 500), dtype=np.uint8) * 255
    
    # Draw a simple table
    # Vertical lines
    cv2.line(img, (100, 50), (100, 450), 0, 2)
    cv2.line(img, (300, 50), (300, 450), 0, 2)
    cv2.line(img, (500, 50), (500, 450), 0, 2)
    
    # Horizontal lines
    cv2.line(img, (100, 50), (500, 50), 0, 2)
    cv2.line(img, (100, 150), (500, 150), 0, 2)
    cv2.line(img, (100, 450), (500, 450), 0, 2)
    
    # Add some text
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, 'Name', (150, 100), font, 0.7, 0, 2)
    cv2.putText(img, 'Age', (350, 100), font, 0.7, 0, 2)
    cv2.putText(img, 'John', (150, 200), font, 0.7, 0, 2)
    cv2.putText(img, '25', (350, 200), font, 0.7, 0, 2)
    
    # Save the image
    os.makedirs('tests/test_data', exist_ok=True)
    cv2.imwrite('tests/test_data/sample_table.png', img)
    return 'tests/test_data/sample_table.png'

@pytest.mark.asyncio
async def test_upload_and_process(authenticated_client):
    """Test the complete document upload and processing flow"""
    # Create sample image
    image_path = create_sample_table_image()
    
    # Test file upload
    with open(image_path, 'rb') as f:
        files = {"file": ("sample_table.png", f, "image/png")}
        response = await authenticated_client.post(
            "/upload/",
            files=files
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "document_id" in data
    document_id = data["document_id"]
    
    # Test processing
    response = await authenticated_client.post(f"/process/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "tables_found" in data
    
    # Test document retrieval
    response = await authenticated_client.get(f"/document/{document_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert "results" in data

@pytest.mark.asyncio
async def test_korean_text(authenticated_client):
    """Test processing Korean text in tables"""
    # Create sample image with Korean text
    img = np.ones((500, 500), dtype=np.uint8) * 255
    
    # Add Korean text using PIL since cv2 doesn't handle Korean well
    from PIL import Image, ImageDraw, ImageFont
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    
    # Add some Korean text
    text = "안녕하세요"
    position = (100, 100)
    draw.text(position, text, font=None, fill=0)
    
    # Convert back to cv2 format
    img = np.array(img_pil)
    
    # Save the image
    test_path = 'tests/test_data/korean_sample.png'
    os.makedirs('tests/test_data', exist_ok=True)
    cv2.imwrite(test_path, img)
    
    # Test file upload
    with open(test_path, 'rb') as f:
        files = {"file": ("korean_sample.png", f, "image/png")}
        response = await authenticated_client.post(
            "/upload/",
            files=files
        )
    
    assert response.status_code == 200
    data = response.json()
    document_id = data["document_id"]
    
    # Test processing
    response = await authenticated_client.post(f"/process/{document_id}")
    assert response.status_code == 200
    
    # Verify Korean text was extracted
    response = await authenticated_client.get(f"/document/{document_id}")
    data = response.json()
    assert data["status"] == "completed"
    assert any("안녕하세요" in str(table["data"]) for table in data["results"])

@pytest.mark.asyncio
async def test_list_documents(authenticated_client):
    """Test listing documents for a user"""
    # List documents (should be empty initially)
    response = await authenticated_client.get("/documents/")
    assert response.status_code == 200
    initial_docs = response.json()
    
    # Upload a document
    image_path = create_sample_table_image()
    with open(image_path, 'rb') as f:
        files = {"file": ("sample_table.png", f, "image/png")}
        await authenticated_client.post("/upload/", files=files)
    
    # List documents again (should have one more document)
    response = await authenticated_client.get("/documents/")
    assert response.status_code == 200
    updated_docs = response.json()
    assert len(updated_docs) == len(initial_docs) + 1

@pytest.mark.asyncio
async def test_unauthorized_access(test_client):
    """Test unauthorized access to document endpoints"""
    # Try to access endpoints without authentication
    endpoints = [
        ("/documents/", "GET"),
        ("/upload/", "POST"),
        ("/document/123", "GET"),
        ("/process/123", "POST")
    ]
    
    for endpoint, method in endpoints:
        if method == "GET":
            response = await test_client.get(endpoint)
        else:
            response = await test_client.post(endpoint)
        
        assert response.status_code in [401, 403], f"Endpoint {endpoint} should require authentication"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])