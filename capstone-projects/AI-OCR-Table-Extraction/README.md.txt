# AI-OCR Table Extraction System

This project automatically extracts tables from documents using OCR and AI.

## Tech Stack
- **Backend**: FastAPI
- **OCR Engines**: PaddleOCR, EasyOCR, Tesseract (with fallback support)
- **Table Detection**: YOLOv8 (with contour-based fallback)
- **Database**: MongoDB
- **Authentication**: JWT with bcrypt
- **Image Processing**: OpenCV

## Prerequisites
- Python 3.8+
- MongoDB running on localhost:27017 (or update MONGODB_URL in .env)
- Tesseract OCR installed (optional, for fallback)

## Installation

1. **Install Python dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
Copy and update `.env` file with your settings:
```bash
MONGODB_URL=mongodb://localhost:27017
DB_NAME=ai_ocr_db
SECRET_KEY=your-secret-key-change-this-in-production
```

3. **Initialize database**:
```bash
python init_db.py
```

## Running the Server

Start the FastAPI server:
```bash
uvicorn Backend.main:app --reload
```

The API will be available at: `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative Docs: `http://localhost:8000/redoc`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Document Processing
- `POST /upload/` - Upload document
- `POST /process/` - Process uploaded document
- `GET /documents/` - List uploaded documents
- `GET /document/{filename}` - Get document details
- `GET /download/{filename}` - Download processed result

### Health Check
- `GET /health` - Check system health

## Testing

Run tests:
```bash
pytest tests/ -v --asyncio-mode=auto
```

## Project Structure

```
AI-OCR-Table-Extraction/
├── Backend/
│   ├── main.py              # FastAPI application
│   ├── routers/             # API route handlers
│   ├── database/            # MongoDB models and connection
│   ├── ocr/                 # OCR engine implementation
│   ├── detection/           # Table detection
│   ├── preprocessing/       # Image preprocessing
│   ├── utils/               # Utilities (auth, logging, etc.)
│   └── converter/           # Data conversion
├── tests/                   # Test suite
├── data/                    # Data directories
│   ├── uploads/            # Uploaded files
│   ├── processed/          # Processed images
│   └── results/            # OCR results
├── models/                  # ML models
├── requirements.txt         # Python dependencies
└── .env                     # Environment variables
```

## Features

- ✅ Multi-engine OCR with graceful fallbacks
- ✅ YOLO-based table detection with fallback
- ✅ Image preprocessing (skew correction, noise removal, contrast enhancement)
- ✅ JWT authentication and authorization
- ✅ MongoDB integration with async support
- ✅ Comprehensive error handling
- ✅ Audit logging
- ✅ Korean and English text support

## Notes

- The system will work even if PaddleOCR, EasyOCR, or YOLO models are not available
- Fallback mechanisms ensure basic functionality is maintained
- For production, update SECRET_KEY and ALLOWED_ORIGINS in .env
