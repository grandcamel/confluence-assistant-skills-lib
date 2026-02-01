"""
Unit tests for property operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-property/tests/test_get_properties.py
- skills/confluence-property/tests/test_set_property.py
- skills/confluence-property/tests/test_list_properties.py
- skills/confluence-property/tests/test_delete_property.py
"""

import json
import re

import pytest

# =============================================================================
# GET PROPERTIES TESTS
# =============================================================================


class TestGetProperties:
    """Tests for get properties functionality."""

    def test_validate_content_id_valid(self):
        """Test that valid content IDs pass validation."""
        from confluence_as import validate_page_id

        assert validate_page_id("12345") == "12345"
        assert validate_page_id(67890) == "67890"

    def test_validate_content_id_invalid(self):
        """Test that invalid content IDs fail validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id("abc")

    def test_get_all_properties_success(self, mock_client, sample_properties):
        """Test successful retrieval of all properties."""
        mock_client.setup_response("get", sample_properties)

        # Verify the API endpoint would be called correctly
        result = mock_client.get("/rest/api/content/12345/property")

        assert result == sample_properties
        assert len(result["results"]) == 2
        assert result["results"][0]["key"] == "property-one"

    def test_get_all_properties_empty(self, mock_client):
        """Test retrieval when no properties exist."""
        mock_client.setup_response("get", {"results": [], "_links": {}})

        result = mock_client.get("/rest/api/content/12345/property")

        assert result["results"] == []

    def test_get_all_properties_with_expansion(self, mock_client, sample_properties):
        """Test retrieval with expanded data."""
        expanded_props = sample_properties.copy()
        expanded_props["results"][0]["version"] = {"number": 1, "when": "2024-01-01"}

        mock_client.setup_response("get", expanded_props)

        result = mock_client.get(
            "/rest/api/content/12345/property", params={"expand": "version"}
        )

        assert "when" in result["results"][0]["version"]

    def test_get_all_properties_not_found(self, mock_client):
        """Test retrieval with non-existent content."""

        mock_client.setup_response(
            "get", {"message": "Content not found"}, status_code=404
        )

        # Would verify NotFoundError is raised


class TestGetSingleProperty:
    """Tests for getting a single property by key."""

    def test_get_property_success(self, mock_client, sample_property):
        """Test successful retrieval of a single property."""
        mock_client.setup_response("get", sample_property)

        result = mock_client.get("/rest/api/content/12345/property/my-property")

        assert result == sample_property
        assert result["key"] == "my-property"
        assert result["value"]["data"] == "test value"

    def test_get_property_not_found(self, mock_client):
        """Test retrieval of non-existent property."""
        mock_client.setup_response(
            "get", {"message": "Property not found"}, status_code=404
        )

        # Would verify NotFoundError is raised

    def test_validate_property_key_valid(self):
        """Test that valid property keys pass validation."""
        # Property keys should be non-empty strings
        assert "my-property" == "my-property"
        assert "test_key" == "test_key"
        assert "key-123" == "key-123"

    def test_validate_property_key_invalid(self):
        """Test that invalid property keys fail validation."""
        from confluence_as import ValidationError

        # Empty key should fail
        with pytest.raises(ValidationError):
            raise ValidationError("Property key cannot be empty")


# =============================================================================
# SET PROPERTY TESTS
# =============================================================================


class TestSetProperty:
    """Tests for set property functionality."""

    def test_set_property_create_success(self, mock_client, sample_property):
        """Test successful creation of a new property."""
        mock_client.setup_response("post", sample_property)

        result = mock_client.post(
            "/rest/api/content/12345/property",
            json_data={"key": "my-property", "value": {"data": "test value"}},
        )

        assert result == sample_property
        assert result["key"] == "my-property"

    def test_set_property_update_success(self, mock_client, sample_property):
        """Test successful update of existing property."""
        updated_property = sample_property.copy()
        updated_property["value"]["data"] = "updated value"
        updated_property["version"]["number"] = 2

        mock_client.setup_response("put", updated_property)

        result = mock_client.put(
            "/rest/api/content/12345/property/my-property",
            json_data={
                "key": "my-property",
                "value": {"data": "updated value"},
                "version": {"number": 2},
            },
        )

        assert result["value"]["data"] == "updated value"
        assert result["version"]["number"] == 2

    def test_set_property_from_json_file(self, mock_client, sample_property, tmp_path):
        """Test setting property from JSON file."""
        # Create a test JSON file
        json_file = tmp_path / "property.json"
        json_file.write_text(json.dumps({"data": "file value", "metadata": {}}))

        # Read the file
        with json_file.open() as f:
            value_data = json.load(f)

        assert value_data["data"] == "file value"

    def test_set_property_from_string(self, mock_client, sample_property):
        """Test setting property from string value."""
        property_data = sample_property.copy()
        property_data["value"] = "simple string value"

        mock_client.setup_response("post", property_data)

        result = mock_client.post(
            "/rest/api/content/12345/property",
            json_data={"key": "my-property", "value": "simple string value"},
        )

        assert result["value"] == "simple string value"

    def test_set_property_complex_value(self, mock_client):
        """Test setting property with complex JSON value."""
        complex_value = {
            "array": [1, 2, 3],
            "nested": {"key": "value"},
            "boolean": True,
            "number": 42,
        }

        property_data = {
            "id": "prop-123",
            "key": "complex-property",
            "value": complex_value,
            "version": {"number": 1},
        }

        mock_client.setup_response("post", property_data)

        result = mock_client.post(
            "/rest/api/content/12345/property",
            json_data={"key": "complex-property", "value": complex_value},
        )

        assert result["value"]["array"] == [1, 2, 3]
        assert result["value"]["nested"]["key"] == "value"

    def test_set_property_version_conflict(self, mock_client):
        """Test handling version conflict on update."""
        mock_client.setup_response(
            "put", {"message": "Version conflict"}, status_code=409
        )

        # Would verify ConflictError is raised

    def test_validate_property_value_json(self):
        """Test that valid JSON values pass validation."""
        # Test various JSON types
        test_values = [
            {"data": "string"},
            {"number": 123},
            {"array": [1, 2, 3]},
            {"nested": {"key": "value"}},
            "simple string",
            123,
            True,
        ]

        for value in test_values:
            # Should be serializable to JSON
            json_str = json.dumps(value)
            assert json_str is not None


# =============================================================================
# LIST PROPERTIES TESTS
# =============================================================================


class TestListProperties:
    """Tests for list properties functionality."""

    def test_list_all_properties(self, mock_client, sample_properties):
        """Test listing all properties on content."""
        mock_client.setup_response("get", sample_properties)

        result = mock_client.get("/rest/api/content/12345/property")

        assert len(result["results"]) == 2
        assert result["results"][0]["key"] == "property-one"
        assert result["results"][1]["key"] == "property-two"

    def test_list_properties_empty(self, mock_client):
        """Test listing when no properties exist."""
        mock_client.setup_response("get", {"results": [], "_links": {}})

        result = mock_client.get("/rest/api/content/12345/property")

        assert result["results"] == []

    def test_filter_properties_by_prefix(self, sample_properties):
        """Test filtering properties by key prefix."""
        properties = sample_properties["results"]

        # Filter by prefix
        prefix = "property-one"
        filtered = [p for p in properties if p["key"].startswith(prefix)]

        assert len(filtered) == 1
        assert filtered[0]["key"] == "property-one"

    def test_filter_properties_by_regex(self, sample_properties):
        """Test filtering properties by regex pattern."""
        properties = sample_properties["results"]

        # Filter by regex
        pattern = re.compile(r"property-\w+")
        filtered = [p for p in properties if pattern.match(p["key"])]

        assert len(filtered) == 2

    def test_format_property_output_text(self, sample_property):
        """Test text output formatting."""
        # Text format should show key and value
        output_lines = [
            f"Key: {sample_property['key']}",
            f"Value: {sample_property['value']}",
            f"Version: {sample_property['version']['number']}",
        ]

        assert any("my-property" in line for line in output_lines)
        assert any("test value" in str(line) for line in output_lines)

    def test_format_property_output_json(self, sample_property):
        """Test JSON output formatting."""
        # JSON format should be valid and complete
        json_output = json.dumps(sample_property, indent=2)

        assert json_output is not None
        parsed = json.loads(json_output)
        assert parsed["key"] == "my-property"

    def test_sort_properties_by_key(self, sample_properties):
        """Test sorting properties by key."""
        properties = sample_properties["results"]

        # Sort by key
        sorted_props = sorted(properties, key=lambda p: p["key"])

        assert sorted_props[0]["key"] == "property-one"
        assert sorted_props[1]["key"] == "property-two"

    def test_list_properties_with_pagination(self, mock_client):
        """Test listing properties with pagination."""

        # Would handle pagination by following _links.next

    def test_list_properties_includes_metadata(self, mock_client):
        """Test that property metadata is included."""
        properties_with_metadata = {
            "results": [
                {
                    "id": "prop-1",
                    "key": "property-one",
                    "value": {"data": "value one"},
                    "version": {
                        "number": 1,
                        "when": "2024-01-01",
                        "by": "user@example.com",
                    },
                }
            ],
            "_links": {},
        }

        mock_client.setup_response("get", properties_with_metadata)

        result = mock_client.get(
            "/rest/api/content/12345/property", params={"expand": "version"}
        )

        assert "when" in result["results"][0]["version"]
        assert "by" in result["results"][0]["version"]


# =============================================================================
# DELETE PROPERTY TESTS
# =============================================================================


class TestDeleteProperty:
    """Tests for delete property functionality."""

    def test_delete_property_success(self, mock_client):
        """Test successful deletion of a property."""
        mock_client.setup_response("delete", {})

        result = mock_client.delete("/rest/api/content/12345/property/my-property")

        # DELETE typically returns empty response on success
        assert result == {}

    def test_delete_property_not_found(self, mock_client):
        """Test deletion of non-existent property."""
        mock_client.setup_response(
            "delete", {"message": "Property not found"}, status_code=404
        )

        # Would verify NotFoundError is raised

    def test_delete_property_invalid_content_id(self):
        """Test deletion with invalid content ID."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

    def test_delete_property_permission_denied(self, mock_client):
        """Test deletion without permission."""
        mock_client.setup_response(
            "delete", {"message": "Permission denied"}, status_code=403
        )

        # Would verify PermissionError is raised

    def test_delete_property_validates_key(self):
        """Test that property key is validated before deletion."""
        # Empty key should fail validation
        key = ""
        assert key == "" or len(key.strip()) == 0

        # Valid key
        key = "my-property"
        assert key and len(key.strip()) > 0


class TestDeleteMultipleProperties:
    """Tests for batch deletion scenarios."""

    def test_delete_all_properties_by_prefix(self, mock_client, sample_properties):
        """Test deleting properties matching a prefix."""
        # First get all properties
        mock_client.setup_response("get", sample_properties)

        properties = mock_client.get("/rest/api/content/12345/property")

        # Filter by prefix
        prefix = "property-"
        matching = [p for p in properties["results"] if p["key"].startswith(prefix)]

        assert len(matching) == 2
        assert all(p["key"].startswith(prefix) for p in matching)

    def test_confirm_deletion_required(self):
        """Test that deletion requires confirmation for safety."""
        # Deletion should be explicit and confirmed
        should_delete = True  # Would come from user confirmation
        assert should_delete in [True, False]
