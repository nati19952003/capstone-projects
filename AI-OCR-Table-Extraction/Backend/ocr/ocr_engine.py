"""Lightweight OCR engine with safe fallbacks.

This module will attempt to use PaddleOCR and EasyOCR when available, but it
won't crash the application if those packages aren't installed. It always
attempts to use pytesseract if present; if no OCR engine is available, it
returns a best-effort placeholder (empty text) so the rest of the pipeline can
continue for testing and uploads.
"""
from typing import List, Dict, Tuple

import numpy as np
import cv2

try:
    from paddleocr import PaddleOCR  # type: ignore
    _HAS_PADDLE = True
except Exception:
    PaddleOCR = None
    _HAS_PADDLE = False

try:
    import easyocr  # type: ignore
    _HAS_EASY = True
except Exception:
    easyocr = None
    _HAS_EASY = False

try:
    import pytesseract  # type: ignore
    _HAS_TESSERACT = True
except Exception:
    pytesseract = None
    _HAS_TESSERACT = False


class OCREngine:
    def __init__(self):
        # Initialize available engines lazily and store configurations
        self.paddle = None
        if _HAS_PADDLE:
            try:
                self.paddle = PaddleOCR(use_angle_cls=True, lang='korean')
            except Exception:
                self.paddle = None

        self.easy = None
        if _HAS_EASY:
            try:
                # easyocr Reader can be heavy and may print to stdout; keep it lazy
                self.easy = easyocr.Reader(['ko', 'en'])
            except Exception:
                self.easy = None

        # Tesseract config: OEM 3 (default) and PSM 6 (assume a block of text)
        self.tesseract_config = r'--oem 3 --psm 6 -l kor+eng'

    def process_image(self, image: np.ndarray) -> List[Dict]:
        """Run available OCR engines and merge results conservatively.

        If multiple engines are available, this routine will collect results
        from each and return them in a simple merged list. For now, the merge
        is conservative: if one engine is available, return its results; if
        multiple are available, concatenate them and let callers handle further
        deduplication.
        """
        results: List[Dict] = []

        # PaddleOCR
        if self.paddle is not None:
            try:
                paddle_res = self._paddle_ocr(image)
                results.extend(paddle_res)
            except Exception:
                pass

        # EasyOCR
        if self.easy is not None:
            try:
                easy_res = self._easy_ocr(image)
                results.extend(easy_res)
            except Exception:
                pass

        # Tesseract
        if _HAS_TESSERACT and pytesseract is not None:
            try:
                tess_res = self._tesseract_ocr(image)
                results.extend(tess_res)
            except Exception:
                pass

        # If no engines produced results, return a placeholder for the whole image
        if not results:
            h, w = (image.shape[0], image.shape[1])
            return [{
                'bbox': [[0, 0], [w, 0], [w, h], [0, h]],
                'text': '',
                'confidence': 0.0,
                'engine': 'none'
            }]

        return results

    def _paddle_ocr(self, image: np.ndarray) -> List[Dict]:
        results: List[Dict] = []
        if self.paddle is None:
            return results

        raw = self.paddle.ocr(image, cls=True)
        for line in raw:
            for bbox, (text, conf) in line:
                results.append({
                    'bbox': bbox,
                    'text': text,
                    'confidence': float(conf) if conf is not None else 0.0,
                    'engine': 'paddle'
                })

        return results

    def _easy_ocr(self, image: np.ndarray) -> List[Dict]:
        results: List[Dict] = []
        if self.easy is None:
            return results

        raw = self.easy.readtext(image)
        for bbox, text, conf in raw:
            results.append({
                'bbox': bbox,
                'text': text,
                'confidence': float(conf) if conf is not None else 0.0,
                'engine': 'easy'
            })

        return results

    def _tesseract_ocr(self, image: np.ndarray) -> List[Dict]:
        results: List[Dict] = []
        if not _HAS_TESSERACT or pytesseract is None:
            return results

        # Use image_to_data to get bounding boxes and confidences
        try:
            data = pytesseract.image_to_data(image, config=self.tesseract_config, output_type=pytesseract.Output.DICT)
        except Exception:
            return results

        n_boxes = len(data.get('text', []))
        for i in range(n_boxes):
            text = data.get('text', [])[i]
            conf_raw = data.get('conf', [])[i]
            try:
                conf = float(conf_raw)
            except Exception:
                try:
                    conf = float(conf_raw) if conf_raw != '' else 0.0
                except Exception:
                    conf = 0.0

            if text is None or text.strip() == '':
                continue

            x = int(data.get('left', [0])[i])
            y = int(data.get('top', [0])[i])
            w = int(data.get('width', [0])[i])
            h = int(data.get('height', [0])[i])

            bbox = [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
            results.append({
                'bbox': bbox,
                'text': text,
                'confidence': conf / 100.0 if conf > 1 else conf,
                'engine': 'tesseract'
            })

        return results