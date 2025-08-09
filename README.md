# FastAPI Vercel Template

FastAPI Vercel Template, UV for dependency management

## Prerequisites

- Python 3.12 or higher
- UV package manager ([Install UV](https://docs.astral.sh/uv/getting-started/installation/))

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd fast-api-vercel-template
```

### 2. Set Up Virtual Environment with UV venv

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate
uv sync
pre-commit install
cp .env.example .env
```

### 3. Development

#### Run the Development Server

```bash
vercel dev
```

The API will be available at `http://localhost:8000`

## UV Commands Reference

### Dependency Management

```bash
# Install all dependencies from pyproject.toml
uv sync

# Install a new dependency
uv add package-name

# Install a development dependency
uv add --dev package-name

# Update dependencies
uv sync --upgrade

# Generate requirements.txt (needed for vercel deploy)
uv pip compile pyproject.toml -o requirements.txt
```

### Running Commands

```bash
# Run a command in the virtual environment
uv run python script.py

# Run with specific Python version
uv run --python 3.12 python script.py

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=api --cov-report=term-missing --cov-report=html:htmlcov

# Run linting
uv run ruff check .
```

## Vercel Deployment

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Deploy to Vercel

```bash
# Login to Vercel (first time only)
vercel login

# Make requirements file (todo, automate)
uv pip compile pyproject.toml -o requirements.txt

# Deploy to production
vercel deploy --prod

```

### 4. Environment Variables

Set environment variables in your Vercel dashboard or using the CLI:

```bash
vercel env add VARIABLE_NAME
```
