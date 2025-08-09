import pytest
from fastapi import HTTPException, status
from unittest.mock import patch
from api.utils.auth import get_api_key, header_scheme


class TestAuth:
    """Test cases for the authentication module."""

    def test_get_api_key_valid(self, valid_api_key):
        """Test successful API key validation."""
        with patch("api.utils.auth.api_key", valid_api_key):
            result = get_api_key(valid_api_key)
            assert result == valid_api_key

    def test_get_api_key_invalid(self, invalid_api_key, valid_api_key):
        """Test failed API key validation."""
        with patch("api.utils.auth.api_key", valid_api_key):
            with pytest.raises(HTTPException) as exc_info:
                get_api_key(invalid_api_key)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"

    def test_get_api_key_empty_env(self):
        """Test behavior when API key is not set in environment."""
        with patch("api.utils.auth.api_key", ""):
            with pytest.raises(HTTPException) as exc_info:
                get_api_key("any-key")

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "x-api-key is not set"

    def test_get_api_key_none_env(self):
        """Test behavior when API key is None in environment."""
        with patch("api.utils.auth.api_key", None):
            with pytest.raises(HTTPException) as exc_info:
                get_api_key("any-key")

            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert exc_info.value.detail == "x-api-key is not set"

    def test_header_scheme_configuration(self):
        """Test that the header scheme is configured correctly."""
        assert header_scheme.name == "x-api-key"
        assert header_scheme.auto_error is True

    def test_get_api_key_with_empty_string(self, valid_api_key):
        """Test API key validation with empty string."""
        with patch("api.utils.auth.api_key", valid_api_key):
            with pytest.raises(HTTPException) as exc_info:
                get_api_key("")

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"

    def test_get_api_key_with_none_value(self, valid_api_key):
        """Test API key validation with None value."""
        with patch("api.utils.auth.api_key", valid_api_key):
            with pytest.raises(HTTPException) as exc_info:
                get_api_key(None)

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"

    def test_get_api_key_case_sensitive(self, valid_api_key):
        """Test that API key validation is case sensitive."""
        with patch("api.utils.auth.api_key", valid_api_key):
            # Test with different case
            with pytest.raises(HTTPException) as exc_info:
                get_api_key(valid_api_key.upper())

            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
            assert exc_info.value.detail == "Could not validate credentials"

    @patch("api.utils.auth.dotenv.load_dotenv")
    @patch("api.utils.auth.os.getenv")
    def test_module_import_behavior(self, mock_getenv, mock_load_dotenv):
        """Test that the module loads environment variables correctly."""
        # Reset the module to test import behavior
        import sys

        if "api.utils.auth" in sys.modules:
            del sys.modules["api.utils.auth"]

        # Mock the environment variable
        mock_getenv.return_value = "test-key"

        # Re-import the module

        # Verify that dotenv.load_dotenv was called
        mock_load_dotenv.assert_called_once()

        # Verify that os.getenv was called with correct parameters
        mock_getenv.assert_called_with("x-api-key", "")
