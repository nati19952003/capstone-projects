# AI OCR Table Extraction System API Documentation

## Overview
The AI OCR Table Extraction System (ATES) is designed to extract structured data from complex document images, with special support for forms containing fixed fields, tables, mixed fonts, and multilingual content (English and Korean).

## Authentication
All API endpoints (except /health and /metrics) require authentication using JWT (JSON Web Token). Users must register and obtain a token before accessing the API.

### 1. Register
```http
POST /auth/register
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "secure_password"
}
```

Response:
```json
{
    "message": "User created successfully"
}
```

### 2. Login
```http
POST /auth/token
Content-Type: application/x-www-form-urlencoded

username=user@example.com&password=secure_password
```

Response:
```json
{
    "access_token": "eyJ0eXAiOiJKV...",
    "token_type": "bearer"
}
```

### 3. Get Current User
```http
GET /auth/me
Authorization: Bearer <your_jwt_token>
```

Response:
```json
{
    "email": "user@example.com",
    "role": "user",
    "permissions": ["upload", "process"]
}
```

## Protected API Endpoints
All endpoints require the following header:
```
Authorization: Bearer <your_jwt_token>
```

### 1. Upload Document
```http
POST /upload/
Content-Type: multipart/form-data

file: <document_image>
```

Response:
```json
{
    "document_id": "507f1f77bcf86cd799439011",
    "status": "uploaded"
}
```

### 2. Process Document
```http
POST /process/{document_id}
```

Response:
```json
{
    "status": "completed",
    "document_id": "507f1f77bcf86cd799439011",
    "tables_found": 2,
    "results": [
        {
            "table_index": 0,
            "data": {
                "headers": ["Name", "Age", "Role"],
                "rows": [
                    {"Name": "John", "Age": "30", "Role": "Manager"},
                    {"Name": "Jane", "Age": "28", "Role": "Developer"}
                ]
            }
        }
    ]
}
```

### 3. Get Document Details
```http
GET /document/{document_id}
```

Response:
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "filename": "document.png",
    "status": "completed",
    "user_id": "507f1f77bcf86cd799439012",
    "created_at": "2023-11-07T10:00:00Z",
    "completed_at": "2023-11-07T10:01:00Z",
    "results": [...],
    "error": null
}
```

### 4. List Documents
```http
GET /documents/
```

Response:
```json
[
    {
        "_id": "507f1f77bcf86cd799439011",
        "filename": "document1.png",
        "status": "completed",
        "created_at": "2023-11-07T10:00:00Z"
    },
    {
        "_id": "507f1f77bcf86cd799439013",
        "filename": "document2.png",
        "status": "processing",
        "created_at": "2023-11-07T10:05:00Z"
    }
]
```

## System Health and Metrics

### 1. Health Check
```http
GET /health
```

Response:
```json
{
    "status": "healthy",
    "database": "connected"
}
```

### 2. System Metrics
```http
GET /metrics
```

Response:
```json
{
    "total_documents_processed": 150,
    "successful_processings": 145,
    "failed_processings": 5,
    "average_processing_time": 12.5,
    "total_uploads": 160
}

## Processing Pipeline

1. **Preprocessing**
   - Skew correction
   - Adaptive noise removal
   - Contrast enhancement
   - Processing time target: <200ms/page

2. **Table Detection**
   - YOLOv8-based detection
   - Handles complex layouts
   - Target accuracy: ≥95%

3. **Text Extraction**
   - Triple-Engine OCR fusion:
     - Tesseract (eng+kor)
     - PaddleOCR (eng+kor)
     - EasyOCR (en+ko)
   - Character-level voting system
   - Target OCR accuracy: ≥95%

4. **Structure Analysis**
   - LayoutLM/TableFormer integration
   - Handles mixed languages
   - Target F1 Score: ≥0.85

## Error Handling

All API endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error responses include detailed messages:
```json
{
    "detail": "Error message description"
}
```

## Rate Limiting
- Maximum 100 requests per minute per IP
- Maximum file size: 10MB
- Supported image formats: PNG, JPG, PDF

## Security Features
- JWT-based authentication
- Role-Based Access Control (RBAC)
- AES-256 encryption for stored data
- HTTPS required for all endpoints