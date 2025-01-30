# Makefile for managing code formatting, styling, and running the main script

# Variables
PYTHON_FILES=.  # Directory or files to format (adjust as needed)

# Targets
.PHONY: help format style black isort clean run tree test coverage

help:
	@echo "Available commands:"
	@echo "  make black       - Format code using black"
	@echo "  make isort       - Sort imports using isort"
	@echo "  make format      - Run both black and isort"
	@echo "  make clean       - Clean up temporary files (e.g., __pycache__)"
	@echo "  make run         - Run the main script"
	@echo "  make tree        - Show directory structure ignoring __pycache__"
	@echo "  make test        - Run tests"
	@echo "  make coverage    - Generate test coverage report"

black:
	@echo "Running black..."
	black $(PYTHON_FILES)

isort:
	@echo "Running isort..."
	isort $(PYTHON_FILES)

format: black isort
	@echo "Code formatting and import sorting completed."

clean:
	@echo "Cleaning up temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@echo "Running the main script..."
	python main.py

tree:
	@echo "Showing directory structure, ignoring __pycache__..."
	tree -I "__pycache__" | pbcopy

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=exp --cov-report=html
