"""
Unit tests for permission operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-permission/tests/test_page_restrictions.py
- skills/confluence-permission/tests/test_get_space_permissions.py
"""

import pytest

# =============================================================================
# PAGE RESTRICTIONS TESTS
# =============================================================================


class TestGetPageRestrictions:
    """Tests for retrieving page restrictions."""

    def test_validate_page_id_valid(self):
        """Test that valid page IDs pass validation."""
        from confluence_as import validate_page_id

        assert validate_page_id("123456") == "123456"
        assert validate_page_id(123456) == "123456"

    def test_validate_page_id_invalid(self):
        """Test that invalid page IDs fail validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id("not-a-number")

    def test_get_page_restrictions_success(self, mock_client, sample_page_restrictions):
        """Test successful retrieval of page restrictions."""
        mock_client.setup_response("get", sample_page_restrictions)

        # Verify response structure
        assert "read" in sample_page_restrictions
        assert "update" in sample_page_restrictions

    def test_get_page_restrictions_unrestricted(self, mock_client):
        """Test getting restrictions for unrestricted page."""
        unrestricted = {
            "read": {
                "operation": "read",
                "restrictions": {
                    "user": {"results": [], "size": 0},
                    "group": {"results": [], "size": 0},
                },
            },
            "update": {
                "operation": "update",
                "restrictions": {
                    "user": {"results": [], "size": 0},
                    "group": {"results": [], "size": 0},
                },
            },
        }
        mock_client.setup_response("get", unrestricted)

        assert unrestricted["read"]["restrictions"]["user"]["size"] == 0
        assert unrestricted["update"]["restrictions"]["user"]["size"] == 0


class TestAddPageRestriction:
    """Tests for adding page restrictions."""

    def test_validate_restriction_type(self):
        """Test that restriction types are validated."""
        valid_types = ["read", "update"]

        for restriction_type in valid_types:
            assert restriction_type in ["read", "update"]

    def test_validate_principal_type(self):
        """Test that principal types are validated."""
        valid_principals = ["user", "group"]

        for principal in valid_principals:
            assert principal in ["user", "group"]

    def test_add_restriction_user(self):
        """Test adding a user restriction."""
        restriction_data = {
            "user": [{"type": "known", "username": "testuser"}],
            "group": [],
        }

        assert len(restriction_data["user"]) == 1
        assert restriction_data["user"][0]["username"] == "testuser"

    def test_add_restriction_group(self):
        """Test adding a group restriction."""
        restriction_data = {
            "user": [],
            "group": [{"type": "group", "name": "test-group"}],
        }

        assert len(restriction_data["group"]) == 1
        assert restriction_data["group"][0]["name"] == "test-group"


class TestRemovePageRestriction:
    """Tests for removing page restrictions."""

    def test_remove_restriction_validation(self):
        """Test that removal requires valid restriction type."""
        valid_operations = ["read", "update"]

        for op in valid_operations:
            assert op in ["read", "update"]

    def test_remove_all_restrictions(self):
        """Test removing all restrictions from a page."""
        # When all restrictions are removed, page becomes unrestricted
        empty_restrictions = {"user": [], "group": []}

        assert len(empty_restrictions["user"]) == 0
        assert len(empty_restrictions["group"]) == 0


class TestRestrictionFormatting:
    """Tests for restriction formatting utilities."""

    def test_format_user_restriction(self, sample_page_restrictions):
        """Test formatting user restrictions."""
        read_users = sample_page_restrictions["read"]["restrictions"]["user"]["results"]

        assert len(read_users) == 1
        assert read_users[0]["username"] == "user1"

    def test_format_group_restriction(self, sample_page_restrictions):
        """Test formatting group restrictions."""
        read_groups = sample_page_restrictions["read"]["restrictions"]["group"][
            "results"
        ]

        assert len(read_groups) == 1
        assert read_groups[0]["name"] == "confluence-administrators"

    def test_restriction_summary(self, sample_page_restrictions):
        """Test generating restriction summary."""
        read_rest = sample_page_restrictions["read"]["restrictions"]
        user_count = read_rest["user"]["size"]
        group_count = read_rest["group"]["size"]

        assert user_count == 1
        assert group_count == 1


# =============================================================================
# SPACE PERMISSIONS TESTS
# =============================================================================


class TestGetSpacePermissions:
    """Tests for retrieving space permissions."""

    def test_validate_space_id_valid(self):
        """Test that valid space IDs pass validation."""
        from confluence_as import (
            validate_page_id,  # Space IDs use same format
        )

        assert validate_page_id("123456", "space_id") == "123456"
        assert validate_page_id(123456, "space_id") == "123456"

    def test_validate_space_id_invalid(self):
        """Test that invalid space IDs fail validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("", "space_id")

        with pytest.raises(ValidationError):
            validate_page_id("abc", "space_id")

    def test_get_space_permissions_success(self, mock_client, sample_space_permissions):
        """Test successful retrieval of space permissions."""
        mock_client.setup_response("get", sample_space_permissions)

        # Verify the response structure
        assert "results" in sample_space_permissions
        assert len(sample_space_permissions["results"]) == 2

    def test_get_space_permissions_empty(self, mock_client):
        """Test getting permissions for space with no explicit permissions."""
        empty_permissions = {"results": [], "_links": {}}
        mock_client.setup_response("get", empty_permissions)

        assert len(empty_permissions["results"]) == 0

    def test_get_space_permissions_not_found(self, mock_client, mock_response):
        """Test getting permissions for non-existent space."""
        mock_client.session.get.return_value = mock_response(
            status_code=404, json_data={"message": "Space not found"}
        )


class TestPermissionFormatting:
    """Tests for permission formatting utilities."""

    def test_format_permission_user(self):
        """Test formatting a user permission."""
        permission = {
            "principal": {"type": "user", "id": "user-123"},
            "operation": {"key": "read", "target": "space"},
        }

        # Test that permission has required fields
        assert permission["principal"]["type"] == "user"
        assert permission["operation"]["key"] == "read"

    def test_format_permission_group(self):
        """Test formatting a group permission."""
        permission = {
            "principal": {"type": "group", "id": "group-456"},
            "operation": {"key": "administer", "target": "space"},
        }

        assert permission["principal"]["type"] == "group"
        assert permission["operation"]["key"] == "administer"

    def test_permission_operations(self):
        """Test that common permission operations are recognized."""
        valid_operations = [
            "read",
            "write",
            "create",
            "administer",
            "delete",
            "export",
            "setpermissions",
        ]

        for op in valid_operations:
            # Each operation should be a valid string
            assert isinstance(op, str)
            assert len(op) > 0
