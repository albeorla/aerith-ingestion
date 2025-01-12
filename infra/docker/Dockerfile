FROM python:3.11.5-slim as base

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.7.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

# Add Poetry to PATH
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Set working directory
WORKDIR $PYSETUP_PATH

# Copy project files
COPY poetry.lock pyproject.toml ./
COPY src/ src/

# Install dependencies
RUN poetry install --no-root --no-dev

# Development stage with test dependencies
FROM base as development
RUN poetry install --no-root

# Test stage
FROM development as test
COPY tests/ tests/
RUN poetry run pytest

# Production stage
FROM base as production
RUN poetry install --no-root --no-dev --no-directory
COPY . .
CMD ["poetry", "run", "start"]