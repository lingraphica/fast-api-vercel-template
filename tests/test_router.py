import pytest
from unittest.mock import patch
from api.routers.model import router


class TestModelRouter:
    """Test cases for the model router."""

    def test_get_models_success(self, client, valid_api_key):
        """Test successful GET request to /api/model/."""
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1

        model = data[0]
        assert "id" in model
        assert "name" in model
        assert "created_at" in model
        assert "updated_at" in model
        assert model["name"] == "Model 1"

    def test_get_models_without_api_key(self, client):
        """Test GET request to /api/model/ without API key."""
        response = client.get("/api/model/")

        assert response.status_code == 422  # Validation error for missing header

    def test_get_models_with_invalid_api_key(self, client, invalid_api_key):
        """Test GET request to /api/model/ with invalid API key."""
        response = client.get("/api/model/", headers={"x-api-key": invalid_api_key})

        assert response.status_code == 401
        assert response.json()["detail"] == "Could not validate credentials"

    @patch("api.routers.model.ModelRead")
    def test_get_models_exception_handling(
        self, mock_model_read, client, valid_api_key
    ):
        """Test GET request to /api/model/ with exception handling."""
        # Mock ModelRead to raise an exception
        mock_model_read.side_effect = Exception("Database error")

        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 500
        assert "Failed to fetch models" in response.json()["detail"]

    def test_router_prefix_and_tags(self):
        """Test that the router has correct prefix and tags."""
        assert router.prefix == "/api/model"
        assert "model" in router.tags

    def test_router_dependencies(self):
        """Test that the router has authentication dependencies."""
        assert len(router.dependencies) == 1
        # The dependency should be the get_api_key function
        assert "get_api_key" in str(router.dependencies[0])

    def test_get_models_response_structure(self, client, valid_api_key):
        """Test that the response structure matches ModelRead schema."""
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        data = response.json()

        # Verify the structure matches ModelRead
        model = data[0]
        required_fields = ["id", "name", "created_at", "updated_at"]
        for field in required_fields:
            assert field in model

    def test_get_models_uuid_format(self, client, valid_api_key):
        """Test that the returned ID is a valid UUID."""
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        data = response.json()
        model = data[0]

        # Verify UUID format
        import uuid

        try:
            uuid.UUID(model["id"])
        except ValueError:
            pytest.fail("Returned ID is not a valid UUID")

    def test_get_models_datetime_format(self, client, valid_api_key):
        """Test that the returned timestamps are valid datetime strings."""
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        data = response.json()
        model = data[0]

        # Verify datetime format
        from datetime import datetime

        try:
            datetime.fromisoformat(model["created_at"].replace("Z", "+00:00"))
            datetime.fromisoformat(model["updated_at"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Returned timestamps are not valid datetime strings")

    def test_get_models_content_type(self, client, valid_api_key):
        """Test that the response has correct content type."""
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

    def test_get_models_empty_response_structure(self, client, valid_api_key):
        """Test that the response is always a list even if empty."""
        # This test verifies the structure, even though the current implementation
        # always returns one item, the structure should be consistent
        response = client.get("/api/model/", headers={"x-api-key": valid_api_key})

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
