.PHONY: help install install-dev test test-unit test-integration run lint format clean setup

help:
	@echo "AI-OCR Table Extraction - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup          - Full setup (install deps, init DB)"
	@echo "  make install        - Install runtime dependencies"
	@echo "  make install-dev    - Install dev dependencies (tests, linting)"
	@echo ""
	@echo "Testing:"
	@echo "  make test           - Run unit tests (no MongoDB required)"
	@echo "  make test-unit      - Run only unit tests (alias for test)"
	@echo "  make test-all       - Run all tests (requires MongoDB)"
	@echo ""
	@echo "Development:"
	@echo "  make run            - Start FastAPI server (requires .env)"
	@echo "  make lint           - Run flake8 linter"
	@echo "  make format         - Format code with black (dry-run)"
	@echo "  make format-fix     - Format code with black (apply changes)"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean          - Remove cache and build artifacts"
	@echo "  make db-init        - Initialize database"

setup: install
	@echo "Setup complete. Run 'make run' to start the server."

install:
	pip install -q -r AI-OCR-Table-Extraction/requirements.txt

install-dev:
	pip install -q -r AI-OCR-Table-Extraction/requirements.txt
	pip install -q flake8 black pytest

test: test-unit

test-unit:
	@echo "Running unit tests (no MongoDB required)..."
	pytest AI-OCR-Table-Extraction/tests -q \
		--ignore=AI-OCR-Table-Extraction/tests/test_auth.py \
		--ignore=AI-OCR-Table-Extraction/tests/test_integration.py -v

test-all:
	@echo "Running all tests (MongoDB must be running)..."
	pytest AI-OCR-Table-Extraction/tests -v

run:
	@echo "Starting FastAPI server..."
	@echo "API will be available at: http://localhost:8000"
	@echo "Interactive docs at: http://localhost:8000/docs"
	cd AI-OCR-Table-Extraction && \
	uvicorn Backend.main:app --reload --host 0.0.0.0 --port 8000

lint:
	flake8 AI-OCR-Table-Extraction/Backend --max-line-length=100

format:
	black --check AI-OCR-Table-Extraction/Backend

format-fix:
	black AI-OCR-Table-Extraction/Backend

clean:
	find AI-OCR-Table-Extraction -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find AI-OCR-Table-Extraction -type f -name "*.pyc" -delete
	rm -rf AI-OCR-Table-Extraction/.pytest_cache
	rm -rf AI-OCR-Table-Extraction/*.egg-info

db-init:
	cd AI-OCR-Table-Extraction && python init_db.py
