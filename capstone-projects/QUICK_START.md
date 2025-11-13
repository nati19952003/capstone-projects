# Quick Start Guide

## Prerequisites
- Python 3.8+
- Git
- (Optional) Docker for MongoDB

## 1. Initial Setup

### Clone & Install
```bash
cd /workspaces/capstone-projects
make install-dev
```

### Configure Environment
```bash
cp AI-OCR-Table-Extraction/.env.example AI-OCR-Table-Extraction/.env
# Edit .env and change SECRET_KEY to a unique value
```

## 2. Run Tests

### Quick Test (No MongoDB Required)
```bash
make test
```

Expected output:
```
10 passed in 1.62s
```

This runs:
- ✅ Preprocessing tests (image enhancement, noise removal, skew correction)
- ✅ Converter tests (CSV, Excel, JSON export)
- ✅ OCR engine structure tests (English, Korean, mixed-language)

### All Tests (Requires MongoDB)
```bash
# Start MongoDB first
docker run -d -p 27017:27017 mongo:latest

# Then run tests
make test-all
```

## 3. Start the Server

```bash
make run
```

The API will be available at:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Example API Calls

**Upload a document:**
```bash
curl -F "file=@sample.png" http://localhost:8000/upload/
```

**Process uploaded document:**
```bash
curl -X POST http://localhost:8000/process/ \
  -H "Content-Type: application/json" \
  -d '{"filename": "sample.png"}'
```

**Run OCR on processed image:**
```bash
curl -X POST http://localhost:8000/ocr/sample.png
```

**List uploaded documents:**
```bash
curl http://localhost:8000/documents/
```

## 4. Code Quality

### Format Code
```bash
make format-fix    # Apply auto-formatting (black)
```

### Lint Code
```bash
make lint          # Check code style (flake8)
```

## 5. Project Structure

```
AI-OCR-Table-Extraction/
├── Backend/
│   ├── main.py              # FastAPI application
│   ├── preprocessing/       # Image preprocessing engine
│   ├── ocr/                 # OCR engine (multi-backend support)
│   ├── detection/           # Table detection
│   ├── converter/           # Output format conversion
│   ├── database/            # MongoDB models
│   ├── routers/             # API route handlers
│   └── utils/               # Auth, logging, metrics
├── tests/                   # Unit tests
├── requirements.txt         # Dependencies
├── .env.example             # Configuration template
└── README.md                # Full documentation
```

## 6. Key Features

- **Multi-engine OCR**: PaddleOCR, EasyOCR, Tesseract with fallbacks
- **Table Detection**: YOLOv8-based detection with contour fallback
- **Image Preprocessing**: Skew correction, noise removal, contrast enhancement
- **Multi-language Support**: English and Korean text recognition
- **JWT Authentication**: Secure API endpoints
- **MongoDB Integration**: Async data persistence

## 7. Troubleshooting

### "ModuleNotFoundError: No module named 'Backend'"
- Run tests from project root directory
- Ensure `tests/conftest.py` exists

### "Secret_KEY is not set" Warning
- Set `SECRET_KEY` in `.env` file
- Or ignore for local development (fallback key used)

### OCR Tests Failing
- Ensure tesseract-ocr system package is installed
- On Linux: `sudo apt-get install tesseract-ocr`
- On Mac: `brew install tesseract`

### MongoDB Connection Error
- Install and start MongoDB: `docker run -d -p 27017:27017 mongo:latest`
- Or skip integration tests: `make test` (unit tests only)

## 8. Next Steps

- Read `FIXES_AND_IMPROVEMENTS.md` for technical details on what was fixed
- Check `Backend/main.py` for FastAPI configuration
- Review `Backend/preprocessing/image_processing.py` for preprocessing pipeline
- Explore OCR engine in `Backend/ocr/ocr_engine.py`

## 9. Contributing

1. Create a branch: `git checkout -b feature/my-feature`
2. Make changes and add tests
3. Run tests: `make test`
4. Format code: `make format-fix`
5. Check linting: `make lint`
6. Push and create a pull request

---

For more details, see [FIXES_AND_IMPROVEMENTS.md](./FIXES_AND_IMPROVEMENTS.md) and the full [README.md](./AI-OCR-Table-Extraction/README.md.txt).
