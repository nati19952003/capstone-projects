from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import shutil
import os
import json
from typing import Dict
import logging
from dotenv import load_dotenv

from .preprocessing.image_processing import PreprocessingEngine
import cv2
from .utils.logging_config import setup_logger

# Setup logging
setup_logger()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AI OCR Table Extraction (preprocessing-only)",
    description="Lightweight server that focuses on image preprocessing and keeps things simple for local testing.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
preprocessor = PreprocessingEngine()

try:
    import pytesseract
    _HAS_OCR = True
except ImportError:
    _HAS_OCR = False
    logger.warning("pytesseract not installed - OCR will be disabled")

# Create required directories
os.makedirs("data/uploads", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "preprocessing-only"}


@app.post("/upload/")
async def upload_document(file: UploadFile = File(...)):
    """Save uploaded file to data/uploads and return the filename for processing."""
    file_path = os.path.join("data", "uploads", file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"filename": file.filename, "status": "uploaded"}

@app.post("/process/")
async def process_document(filename: str):
    """Process a previously uploaded file by filename using the preprocessing engine.

    The endpoint writes a processed image to `data/processed/{filename}` and
    returns basic metadata so you can verify preprocessing worked.
    """
    file_path = os.path.join("data", "uploads", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    img = cv2.imread(file_path)
    if img is None:
        raise HTTPException(status_code=400, detail="Could not read image")

    processed_image = preprocessor.process(img)

    # Save processed image as PNG
    processed_path = os.path.join("data", "processed", f"{filename}.png")
    cv2.imwrite(processed_path, processed_image)

    return {
        "status": "processed",
        "filename": filename,
        "processed_path": processed_path,
        "shape": processed_image.shape
    }

@app.get("/documents/")
async def list_documents():
    """Return list of uploaded filenames for quick inspection."""
    files = os.listdir(os.path.join("data", "uploads"))
    return {"uploads": files}

@app.get("/document/{filename}")
async def get_document(filename: str):
    """Return processed results (JSON) if available, otherwise raw upload info."""
    result_path = os.path.join("data", "processed", f"{filename}.png")
    if os.path.exists(result_path):
        return {"filename": filename, "processed_path": result_path}

    upload_path = os.path.join("data", "uploads", filename)
    if os.path.exists(upload_path):
        return {"filename": filename, "uploaded_path": upload_path}

    raise HTTPException(status_code=404, detail="File not found")

@app.post("/ocr/{filename}")
async def perform_ocr(filename: str):
    """Perform OCR on a processed image."""
    if not _HAS_OCR:
        raise HTTPException(status_code=400, detail="OCR is not available - please install pytesseract")

    # Get the processed image
    processed_path = os.path.join("data", "processed", f"{filename}.png")
    if not os.path.exists(processed_path):
        raise HTTPException(status_code=404, detail="Processed file not found - process the image first")

    try:
        # Read image
        img = cv2.imread(processed_path)
        if img is None:
            raise HTTPException(status_code=400, detail="Could not read processed image")

        # Convert to RGB for better OCR
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Perform OCR
        ocr_result = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT)
        
        # Format results - collect words with confidence
        text_results = []
        n_boxes = len(ocr_result['text'])
        for i in range(n_boxes):
            text = ocr_result['text'][i].strip()
            conf = int(ocr_result['conf'][i])
            
            if text and conf > 0:  # Filter empty text and low confidence
                x, y, w, h = (
                    ocr_result['left'][i],
                    ocr_result['top'][i],
                    ocr_result['width'][i],
                    ocr_result['height'][i]
                )
                text_results.append({
                    'text': text,
                    'confidence': conf,
                    'bbox': [x, y, x + w, y + h]
                })

        return {
            'filename': filename,
            'text_blocks': text_results,
            'word_count': len(text_results)
        }

    except Exception as e:
        logger.error(f"OCR failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"OCR failed: {str(e)}")

@app.get("/download/{filename}")
async def download_result(filename: str):
    """Return the processed image file if present."""
    result_path = os.path.join("data", "processed", f"{filename}.png")
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="Processed file not found")

    return JSONResponse({"processed_path": result_path})
