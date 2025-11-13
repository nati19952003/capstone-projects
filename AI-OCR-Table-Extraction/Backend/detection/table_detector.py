"""Table detection with a safe fallback when heavy dependencies are missing.

This module prefers to use ultralytics.YOLO if available, but falls back to a
lightweight contour-based or full-image detector when the package/model is not
installed. This keeps the app runnable on systems without GPU/YOLO installed.
"""
import cv2
import numpy as np
from typing import List, Tuple

try:
    from ultralytics import YOLO  # type: ignore
    _HAS_YOLO = True
except Exception:
    YOLO = None
    _HAS_YOLO = False


class TableDetector:
    def __init__(self, model_path: str = "models/table_detection.pt"):
        """Initialize detector. If YOLO is available it will be used; otherwise
        a lightweight fallback is used.
        """
        self.use_yolo = _HAS_YOLO
        if self.use_yolo:
            try:
                self.model = YOLO(model_path)
            except Exception:
                # If model file isn't present or fails to load, disable YOLO
                self.use_yolo = False
                self.model = None
        else:
            self.model = None

    def detect_tables(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Return list of bounding boxes (x1,y1,x2,y2).

        If YOLO is available it will be used; otherwise, perform a simple
        contour-based detection for large rectangular areas, and if that
        fails, return one box covering the whole image.
        """
        h, w = image.shape[:2]

        if self.use_yolo and self.model is not None:
            try:
                results = self.model(image)
                boxes = []
                for r in results:
                    for box in r.boxes:
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        boxes.append((int(x1), int(y1), int(x2), int(y2)))
                if boxes:
                    return boxes
            except Exception:
                # Fall through to fallback detector
                pass

        # Fallback: simple contour detection for large rectangular shapes
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if image.ndim == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes = []
        for cnt in contours:
            x, y, cw, ch = cv2.boundingRect(cnt)
            area = cw * ch
            if area > (w * h) * 0.01:  # ignore very small contours
                # Filter for rectangular-ish shapes
                approx = cv2.approxPolyDP(cnt, 0.02 * cv2.arcLength(cnt, True), True)
                if len(approx) >= 4:
                    boxes.append((x, y, x + cw, y + ch))

        if boxes:
            # Optionally sort by area descending
            boxes = sorted(boxes, key=lambda b: (b[2] - b[0]) * (b[3] - b[1]), reverse=True)
            return boxes

        # Last-resort: return full-image box
        return [(0, 0, w, h)]

    def extract_table_regions(self, image: np.ndarray, boxes: List[Tuple[int, int, int, int]]) -> List[np.ndarray]:
        """Crop regions from the image corresponding to boxes."""
        table_regions = []
        for box in boxes:
            x1, y1, x2, y2 = box
            # clamp coordinates
            x1 = max(0, int(x1))
            y1 = max(0, int(y1))
            x2 = min(image.shape[1], int(x2))
            y2 = min(image.shape[0], int(y2))
            if x2 > x1 and y2 > y1:
                table_region = image[y1:y2, x1:x2]
                table_regions.append(table_region)

        return table_regions