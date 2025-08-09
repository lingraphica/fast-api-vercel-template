import pytest
import uuid
from datetime import datetime
from pydantic import ValidationError
from api.models.model import (
    ModelBase,
    ModelCreate,
    ModelRead,
    ModelUpdate,
    ModelDelete,
    Model,
    ModelResponse,
)


class TestModelBase:
    """Test cases for the ModelBase model."""

    def test_model_base_valid(self):
        """Test valid ModelBase creation."""
        model_id = uuid.uuid4()
        model = ModelBase(id=model_id, name="Test Model")

        assert model.id == model_id
        assert model.name == "Test Model"

    def test_model_base_default_id(self):
        """Test ModelBase creation with default UUID."""
        model = ModelBase(name="Test Model")

        assert isinstance(model.id, uuid.UUID)
        assert model.name == "Test Model"

    def test_model_base_name_validation_min_length(self):
        """Test ModelBase name validation - minimum length."""
        with pytest.raises(ValidationError) as exc_info:
            ModelBase(name="")

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_model_base_name_validation_max_length(self):
        """Test ModelBase name validation - maximum length."""
        long_name = "a" * 256  # 256 characters
        with pytest.raises(ValidationError) as exc_info:
            ModelBase(name=long_name)

        assert "String should have at most 255 characters" in str(exc_info.value)

    def test_model_base_name_required(self):
        """Test that name is required in ModelBase."""
        with pytest.raises(ValidationError) as exc_info:
            ModelBase()

        assert "Field required" in str(exc_info.value)


class TestModelCreate:
    """Test cases for the ModelCreate model."""

    def test_model_create_valid(self):
        """Test valid ModelCreate creation."""
        model = ModelCreate(name="Test Model")

        assert isinstance(model.id, uuid.UUID)
        assert model.name == "Test Model"

    def test_model_create_inherits_validation(self):
        """Test that ModelCreate inherits validation from ModelBase."""
        with pytest.raises(ValidationError):
            ModelCreate(name="")  # Should fail due to min_length validation


class TestModelRead:
    """Test cases for the ModelRead model."""

    def test_model_read_valid(self):
        """Test valid ModelRead creation."""
        model_id = uuid.uuid4()
        now = datetime.now()
        model = ModelRead(
            id=model_id, name="Test Model", created_at=now, updated_at=now
        )

        assert model.id == model_id
        assert model.name == "Test Model"
        assert model.created_at == now
        assert model.updated_at == now

    def test_model_read_required_fields(self):
        """Test that all fields are required in ModelRead."""
        with pytest.raises(ValidationError) as exc_info:
            ModelRead(name="Test Model")

        assert "Field required" in str(exc_info.value)

    def test_model_read_config(self):
        """Test that ModelRead has correct configuration."""
        assert hasattr(ModelRead, "Config")
        assert hasattr(ModelRead.Config, "from_attributes")


class TestModelUpdate:
    """Test cases for the ModelUpdate model."""

    def test_model_update_all_fields(self):
        """Test ModelUpdate with all fields."""
        model = ModelUpdate(name="Updated Model", description="Updated description")

        assert model.name == "Updated Model"
        assert model.description == "Updated description"

    def test_model_update_partial_fields(self):
        """Test ModelUpdate with partial fields."""
        model = ModelUpdate(name="Updated Model")

        assert model.name == "Updated Model"
        assert model.description is None

    def test_model_update_empty(self):
        """Test ModelUpdate with no fields."""
        model = ModelUpdate()

        assert model.name is None
        assert model.description is None

    def test_model_update_name_validation(self):
        """Test ModelUpdate name validation."""
        with pytest.raises(ValidationError) as exc_info:
            ModelUpdate(name="")

        assert "String should have at least 1 character" in str(exc_info.value)

    def test_model_update_name_max_length(self):
        """Test ModelUpdate name maximum length validation."""
        long_name = "a" * 256
        with pytest.raises(ValidationError) as exc_info:
            ModelUpdate(name=long_name)

        assert "String should have at most 255 characters" in str(exc_info.value)


class TestModelDelete:
    """Test cases for the ModelDelete model."""

    def test_model_delete_valid(self):
        """Test valid ModelDelete creation."""
        model_id = uuid.uuid4()
        model = ModelDelete(id=model_id)

        assert model.id == model_id

    def test_model_delete_required_id(self):
        """Test that id is required in ModelDelete."""
        with pytest.raises(ValidationError) as exc_info:
            ModelDelete()

        assert "Field required" in str(exc_info.value)


class TestModel:
    """Test cases for the Model model."""

    def test_model_valid(self):
        """Test valid Model creation."""
        model_id = uuid.uuid4()
        now = datetime.now()
        model = Model(id=model_id, name="Test Model", created_at=now, updated_at=now)

        assert model.id == model_id
        assert model.name == "Test Model"
        assert model.created_at == now
        assert model.updated_at == now

    def test_model_config(self):
        """Test that Model has correct configuration."""
        assert hasattr(Model, "Config")
        assert hasattr(Model.Config, "from_attributes")


class TestModelResponse:
    """Test cases for the ModelResponse model."""

    def test_model_response_valid(self):
        """Test valid ModelResponse creation."""
        model_id = uuid.uuid4()
        now = datetime.now()
        model_instance = Model(
            id=model_id, name="Test Model", created_at=now, updated_at=now
        )

        response = ModelResponse(model=model_instance)

        assert response.model == model_instance
        assert response.model.id == model_id
        assert response.model.name == "Test Model"

    def test_model_response_required_model(self):
        """Test that model is required in ModelResponse."""
        with pytest.raises(ValidationError) as exc_info:
            ModelResponse()

        assert "Field required" in str(exc_info.value)


class TestModelIntegration:
    """Integration tests for model interactions."""

    def test_model_creation_flow(self):
        """Test the complete model creation flow."""
        # Create a base model
        base_model = ModelBase(name="Integration Test Model")

        # Create a model instance with timestamps
        now = datetime.now()
        model_instance = Model(
            id=base_model.id, name=base_model.name, created_at=now, updated_at=now
        )

        # Create a response
        response = ModelResponse(model=model_instance)

        # Verify the flow
        assert response.model.name == "Integration Test Model"
        assert response.model.id == base_model.id
        assert response.model.created_at == now
        assert response.model.updated_at == now

    def test_model_update_flow(self):
        """Test the model update flow."""
        # Create original model
        original_model = Model(
            id=uuid.uuid4(),
            name="Original Name",
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        print(original_model)

        # Create update
        update = ModelUpdate(name="Updated Name", description="New description")

        # Simulate applying update (this would be done in business logic)
        # For testing, we just verify the update object is valid
        assert update.name == "Updated Name"
        assert update.description == "New description"

    def test_model_serialization(self):
        """Test that models can be serialized to dict."""
        model_id = uuid.uuid4()
        now = datetime.now()
        model = Model(
            id=model_id, name="Serialization Test", created_at=now, updated_at=now
        )

        # Convert to dict
        model_dict = model.model_dump()

        assert model_dict["id"] == str(model_id)
        assert model_dict["name"] == "Serialization Test"
        assert "created_at" in model_dict
        assert "updated_at" in model_dict
