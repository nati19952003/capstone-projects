import pytest
import cv2
import numpy as np
import os
from Backend.preprocessing.image_processing import preprocess_image, enhance_image

@pytest.fixture
def sample_image():
    # Create a sample image for testing
    img = np.zeros((100, 100), dtype=np.uint8)
    cv2.putText(img, "Test", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 255, 2)
    return img

def test_preprocess_image(tmp_path, sample_image):
    # Save sample image
    image_path = os.path.join(tmp_path, "test.png")
    cv2.imwrite(image_path, sample_image)
    
    # Test preprocessing
    result = preprocess_image(image_path)
    
    assert isinstance(result, np.ndarray)
    assert result.shape == sample_image.shape
    assert result.dtype == np.uint8

def test_enhance_image(sample_image):
    # Test image enhancement
    result = enhance_image(sample_image)
    
    assert isinstance(result, np.ndarray)
    assert result.shape == sample_image.shape
    assert result.dtype == np.uint8