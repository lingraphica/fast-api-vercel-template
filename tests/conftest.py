import pytest
import os
from fastapi.testclient import TestClient
from api.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def valid_api_key():
    """Provide a valid API key for testing."""
    return "test-api-key-123"


@pytest.fixture
def invalid_api_key():
    """Provide an invalid API key for testing."""
    return "invalid-api-key"


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables."""
    # Set a test API key
    os.environ["x-api-key"] = "test-api-key-123"
    yield
    # Clean up after tests
    if "x-api-key" in os.environ:
        del os.environ["x-api-key"]
