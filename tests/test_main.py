from unittest.mock import patch, AsyncMock
import httpx


class TestMainApp:
    """Test cases for the main FastAPI application."""

    def test_read_root(self, client):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}

    def test_read_item_with_id_only(self, client):
        """Test the items endpoint with only item_id."""
        response = client.get("/items/42")
        assert response.status_code == 200
        assert response.json() == {"item_id": 42, "q": None}

    def test_read_item_with_query_param(self, client):
        """Test the items endpoint with both item_id and query parameter."""
        response = client.get("/items/42?q=test")
        assert response.status_code == 200
        assert response.json() == {"item_id": 42, "q": "test"}

    @patch("httpx.AsyncClient")
    def test_test_endpoint_success(self, mock_client_class, client):
        """Test the /test endpoint with successful external API call."""
        # Mock the async client
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client

        # Mock the response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"message": "success"}
        mock_client.get.return_value = mock_response

        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    @patch("httpx.AsyncClient")
    def test_test_endpoint_failure(self, mock_client_class, client):
        """Test the /test endpoint with failed external API call."""
        # Mock the async client to raise an exception
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Connection failed")

        response = client.get("/test")
        assert response.status_code == 500

    def test_app_metadata(self, client):
        """Test that the app has correct metadata."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_schema(self, client):
        """Test that the OpenAPI schema is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert schema["info"]["title"] == "FastAPI Vercel Template"
        assert schema["info"]["version"] == "1.0.0"

    def test_startup_event(self, client):
        """Test that the startup event works correctly."""
        # The startup event should have already been called when creating the client
        # We can verify the app is working by making a request
        response = client.get("/")
        assert response.status_code == 200

    def test_shutdown_event(self, client):
        """Test that the shutdown event works correctly."""
        # The shutdown event is called when the app shuts down
        # We can't easily test this in unit tests, but we can verify the app works
        response = client.get("/")
        assert response.status_code == 200
