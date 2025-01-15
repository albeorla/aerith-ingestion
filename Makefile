.PHONY: install install-hooks format lint check clean tree-src tree-docs help serve sync viz diagrams crawl precrawl

#######################
# Core Setup
#######################

# Poetry installation and environment setup
install:
	@echo "Installing dependencies..."
	poetry install || (poetry lock && poetry install)
	@if [ ! -x .git/hooks/pre-commit ] || [ ! -x .git/hooks/prepare-commit-msg ] || \
		! cmp -s hooks/pre-commit .git/hooks/pre-commit || \
		! cmp -s hooks/prepare-commit-msg .git/hooks/prepare-commit-msg; then \
		echo "Git hooks need to be installed or updated..."; \
		$(MAKE) install-hooks; \
	else \
		echo "Git hooks are up to date"; \
	fi

# Install git hooks
install-hooks:
	@echo "Setting up git hooks..."
	@mkdir -p .git/hooks
	@cp hooks/prepare-commit-msg .git/hooks/
	@chmod +x .git/hooks/prepare-commit-msg
	@cp hooks/pre-commit .git/hooks/
	@chmod +x .git/hooks/pre-commit
	@ls -l .git/hooks/prepare-commit-msg .git/hooks/pre-commit
	@echo "✓ Git hooks installed successfully"

#######################
# Main Application
#######################

# Run the API server
serve:
	@echo "Starting the API server..."
	poetry run aerith serve

# Sync Todoist tasks
sync:
	@echo "Syncing Todoist tasks..."
	poetry run aerith sync

# Crawl a website (with optional precrawl) and save results
crawl: URL := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
crawl:
	@echo "Crawling a website and saving results..."
	poetry run aerith crawl $(URL)
%:
	@:

#######################
# Development Tools
#######################

# Format the code
format:
	@echo "Formatting code..."
	poetry run pycln src docs infra hooks 
	poetry run isort src docs infra hooks 
	poetry run black src docs infra hooks 

# Lint the code
lint:
	@echo "Linting code..."
	poetry run flake8 src infra hooks

# Check code quality without modifying files
check:
	@echo "Checking code quality..."
	poetry run pycln --check src docs infra hooks
	poetry run isort --check-only src docs infra hooks
	poetry run black --check src docs infra hooks
	poetry run flake8 src infra hooks

#######################
# Visualization & Documentation
#######################

# Generate vector visualization
viz:
	@echo "Generating vector visualization..."
	poetry run aerith viz

# Generate code structure diagrams
diagrams:
	@echo "Generating code structure diagrams..."
	@mkdir -p docs/diagrams
	poetry run pymermaider src/aerith_ingestion -o docs/diagrams --exclude "**/tests/**"

#######################
# Utility & Maintenance
#######################

# Clean up generated files and directories
clean:
	@echo "Cleaning up..."
	rm -rf .pytest_cache .coverage htmlcov dist *.egg-info logs/
	find . -type d -name __pycache__ -exec rm -rf {} +

# Display directory structure considering .gitignore
tree-src:
	@echo "Displaying source directory structure..."
	git ls-files --others --exclude-standard --cached --directory | grep -E '^src/' | tree --fromfile

tree-docs:
	@echo "Displaying docs directory structure..."
	git ls-files --others --exclude-standard --cached --directory | grep -E '^docs/' | tree --fromfile

# Display available commands
help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies using Poetry"
	@echo "  make install-hooks- Install git hooks"
	@echo "  make serve        - Run the API server"
	@echo "  make sync         - Sync Todoist tasks"
	@echo "  make crawl        - Crawl a website and save results (--url URL --output FILE)"
	@echo "  make format       - Format code with pycln, isort, and black"
	@echo "  make lint         - Lint code with flake8"
	@echo "  make check        - Check code quality without modifying files"
	@echo "  make viz          - Generate vector visualization"
	@echo "  make diagrams     - Generate code structure diagrams using pymermaider"
	@echo "  make clean        - Clean up generated files and directories"
	@echo "  make tree-src     - Display source directory structure"
	@echo "  make tree-docs    - Display docs directory structure"