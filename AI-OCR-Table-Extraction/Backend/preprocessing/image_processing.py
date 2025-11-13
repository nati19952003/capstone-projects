import cv2
import numpy as np
from typing import Tuple
import time

class PreprocessingEngine:
    def __init__(self):
        """
        Initialize the preprocessing engine with default parameters
        """
        self.gaussian_kernel = (5, 5)
        self.median_kernel = 3
        self.max_processing_time = 0.2  # 200ms target

    def process(self, image: np.ndarray) -> np.ndarray:
        """
        Main preprocessing pipeline
        """
        start_time = time.time()
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
            
        # Apply skew correction
        corrected = self._correct_skew(gray)
        
        # Apply noise removal
        denoised = self._remove_noise(corrected)
        
        # Apply contrast enhancement
        enhanced = self._enhance_contrast(denoised)
        
        # Verify processing time
        processing_time = time.time() - start_time
        if processing_time > self.max_processing_time:
            print(f"Warning: Processing time ({processing_time:.3f}s) exceeded target (0.2s)")
        
        return enhanced

    def _correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Detect and correct image skew
        """
        # Find all contours
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
        
        if lines is not None:
            # Calculate the dominant angle
            angles = []
            for line in lines:
                rho, theta = line[0]
                angle = theta * 180 / np.pi
                if abs(angle) < 45:  # Consider only reasonable angles
                    angles.append(angle)
            
            if angles:
                median_angle = np.median(angles)
                if abs(median_angle) > 0.5:  # Only correct if skew is significant
                    # Rotate image
                    center = tuple(np.array(image.shape[1::-1]) / 2)
                    mat = cv2.getRotationMatrix2D(center, median_angle, 1.0)
                    return cv2.warpAffine(image, mat, image.shape[1::-1],
                                        flags=cv2.INTER_CUBIC,
                                        borderMode=cv2.BORDER_REPLICATE)
        
        return image

    def _remove_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Adaptive noise removal using both Gaussian and Median filtering
        """
        # Calculate image statistics
        mean, std = cv2.meanStdDev(image)
        
        # If high noise (high std), apply stronger filtering
        if std > 30:
            # Apply Gaussian for general noise
            blurred = cv2.GaussianBlur(image, self.gaussian_kernel, 0)
            # Apply Median for salt-and-pepper noise
            denoised = cv2.medianBlur(blurred, self.median_kernel)
        else:
            # For cleaner images, use lighter filtering
            denoised = cv2.GaussianBlur(image, (3, 3), 0)
        
        return denoised

    def _enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance contrast using adaptive histogram equalization
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        
        return enhanced

    def get_processing_info(self, image: np.ndarray) -> Tuple[float, dict]:
        """
        Get processing time and quality metrics
        """
        start_time = time.time()
        processed = self.process(image)
        processing_time = time.time() - start_time
        
        # Calculate quality metrics
        metrics = {
            'mean_value': np.mean(processed),
            'std_dev': np.std(processed),
            'processing_time': processing_time
        }
        
        return processed, metrics