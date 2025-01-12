.PHONY: install lint format clean tree help start check

# Poetry installation and environment setup
install:
	poetry install || (poetry lock && poetry install)

# Format the code
format:
	poetry run pycln src docs infra
	poetry run isort src docs infra
	poetry run black src docs infra

# Lint the code
lint:
	poetry run flake8 src infra

# Check code quality without modifying files
check:
	poetry run pycln --check src docs infra
	poetry run isort --check-only src docs infra
	poetry run black --check src docs infra
	poetry run flake8 src infra

# Clean up generated files and directories
clean:
	rm -rf .pytest_cache .coverage htmlcov dist *.egg-info logs/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Display directory structure considering .gitignore
tree-src:
	git ls-files --others --exclude-standard --cached --directory | grep -E '^src/' | tree --fromfile

tree-docs:
	git ls-files --others --exclude-standard --cached --directory | grep -E '^docs/' | tree --fromfile

# Display available commands
help:
	@echo "Available commands:"
	@echo "  make install  - Install dependencies using Poetry"
	@echo "  make format   - Format code with pycln, isort, and black"
	@echo "  make lint     - Lint code with flake8"
	@echo "  make check    - Check code quality without modifying files"
	@echo "  make clean    - Clean up generated files and directories"
	@echo "  make tree-src - Display source directory structure"
	@echo "  make tree-docs- Display docs directory structure"
	@echo "  make start    - Run the application"

# Run the application
start:
	poetry run start
