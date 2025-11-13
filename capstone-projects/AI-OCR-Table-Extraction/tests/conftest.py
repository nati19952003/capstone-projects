import os
import sys

# Ensure the package directory (AI-OCR-Table-Extraction) is on sys.path so tests
# can import the `Backend` package using plain "Backend.*" imports.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
