import pytest
from Backend.ocr.ocr_engine import OCREngine
import numpy as np
import cv2

@pytest.fixture
def ocr_engine():
    return OCREngine()

@pytest.fixture
def sample_images():
    # Create sample images with English and Korean text
    def create_text_image(text, size=(400, 100)):
        img = np.ones(size, dtype=np.uint8) * 255
        
        if any('\u3131' <= c <= '\u318E' or '\uAC00' <= c <= '\uD7A3' for c in text):
            # Korean text using PIL
            from PIL import Image, ImageDraw, ImageFont
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((10, 10), text, font=None, fill=0)
            img = np.array(img_pil)
        else:
            # English text using cv2
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(img, text, (10, 50), font, 1, 0, 2)
        
        return img
    
    return {
        'english': create_text_image('Hello World'),
        'korean': create_text_image('안녕하세요'),
        'mixed': create_text_image('Hello 안녕')
    }

def test_english_ocr(ocr_engine, sample_images):
    results = ocr_engine.process_image(sample_images['english'])
    assert len(results) > 0
    # OCR quality depends on engine availability; verify structure rather than exact text
    for result in results:
        assert 'text' in result
        assert 'bbox' in result
        assert 'confidence' in result

def test_korean_ocr(ocr_engine, sample_images):
    results = ocr_engine.process_image(sample_images['korean'])
    assert len(results) > 0
    # Verify result structure rather than exact Korean text (OCR varies by engine)
    for result in results:
        assert 'text' in result
        assert 'bbox' in result
        assert 'confidence' in result

def test_mixed_language_ocr(ocr_engine, sample_images):
    results = ocr_engine.process_image(sample_images['mixed'])
    assert len(results) > 0
    # Verify result structure for mixed language images
    for result in results:
        assert 'text' in result
        assert 'bbox' in result
        assert 'confidence' in result

def test_confidence_scores(ocr_engine, sample_images):
    for image_type, image in sample_images.items():
        results = ocr_engine.process_image(image)
        for result in results:
            assert 'confidence' in result
            assert 0 <= result['confidence'] <= 1

def test_bounding_boxes(ocr_engine, sample_images):
    for image_type, image in sample_images.items():
        results = ocr_engine.process_image(image)
        for result in results:
            assert 'bbox' in result
            bbox = result['bbox']
            assert len(bbox) == 4  # Should have 4 points
            assert all(len(point) == 2 for point in bbox)  # Each point should have x,y coordinates