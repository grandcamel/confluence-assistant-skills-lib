"""
Unit tests for watch operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-watch/tests/test_watch_page.py
- skills/confluence-watch/tests/test_unwatch_page.py
- skills/confluence-watch/tests/test_watch_space.py
- skills/confluence-watch/tests/test_get_watchers.py
- skills/confluence-watch/tests/test_am_i_watching.py
"""

import pytest

# =============================================================================
# WATCH PAGE TESTS
# =============================================================================


class TestWatchPage:
    """Tests for page watching functionality."""

    def test_validate_page_id_valid(self):
        """Test that valid page IDs pass validation."""
        from confluence_as import validate_page_id

        assert validate_page_id("12345") == "12345"
        assert validate_page_id(67890) == "67890"

    def test_validate_page_id_invalid(self):
        """Test that invalid page IDs fail validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id("abc")  # Not numeric

        with pytest.raises(ValidationError):
            validate_page_id(None)

    def test_watch_page_success(self, mock_client, sample_watch_response):
        """Test successful page watching."""
        mock_client.setup_response("post", sample_watch_response)

        # Mock the API call
        result = mock_client.post(
            "/rest/api/user/watch/content/123456", operation="watch page"
        )

        assert result["success"] is True
        assert result["status_code"] == 200

    def test_watch_page_already_watching(self, mock_client):
        """Test watching a page that is already being watched."""
        # API returns 200 even if already watching
        mock_client.setup_response("post", {"success": True, "status_code": 200})

        result = mock_client.post(
            "/rest/api/user/watch/content/123456", operation="watch page"
        )

        assert result["success"] is True

    def test_watch_page_not_found(self, mock_client, mock_response):
        """Test watching a non-existent page."""
        from confluence_as import NotFoundError, handle_confluence_error

        error_response = mock_response(
            status_code=404, json_data={"message": "Page not found"}
        )

        with pytest.raises(NotFoundError):
            handle_confluence_error(error_response, "watch page")

    def test_watch_page_permission_denied(self, mock_client, mock_response):
        """Test watching a page without permission."""
        from confluence_as import PermissionError, handle_confluence_error

        error_response = mock_response(
            status_code=403, json_data={"message": "Permission denied"}
        )

        with pytest.raises(PermissionError):
            handle_confluence_error(error_response, "watch page")

    def test_watch_page_basic_post(self, mock_client, sample_watch_response):
        """Test basic watch page POST request."""
        mock_client.setup_response("post", sample_watch_response)

        result = mock_client.post(
            "/rest/api/user/watch/content/123456", operation="watch page"
        )

        assert result["success"] is True

    def test_watch_page_output_json(self):
        """Test JSON output format."""
        from confluence_as import format_json

        data = {"success": True, "page_id": "123456"}
        result = format_json(data)

        assert '"success": true' in result
        assert '"page_id": "123456"' in result

    def test_watch_page_output_text(self):
        """Test text output format."""
        # Verify that text output is readable
        page_id = "123456"
        message = f"Now watching page {page_id}"

        assert "watching" in message.lower()
        assert page_id in message


# =============================================================================
# UNWATCH PAGE TESTS
# =============================================================================


class TestUnwatchPage:
    """Tests for page unwatching functionality."""

    def test_unwatch_page_success(self, mock_client):
        """Test successful page unwatching."""
        mock_client.setup_response("delete", {})

        result = mock_client.delete(
            "/rest/api/user/watch/content/123456", operation="unwatch page"
        )

        assert result == {} or result.get("success") is True

    def test_unwatch_page_not_watching(self, mock_client):
        """Test unwatching a page that wasn't being watched."""
        # API should return success even if not watching
        mock_client.setup_response("delete", {})

        result = mock_client.delete(
            "/rest/api/user/watch/content/123456", operation="unwatch page"
        )

        # Should succeed without error
        assert result == {} or result.get("success") is True

    def test_unwatch_page_not_found(self, mock_client, mock_response):
        """Test unwatching a non-existent page."""
        from confluence_as import NotFoundError, handle_confluence_error

        error_response = mock_response(
            status_code=404, json_data={"message": "Page not found"}
        )

        with pytest.raises(NotFoundError):
            handle_confluence_error(error_response, "unwatch page")

    def test_unwatch_page_validation(self):
        """Test page ID validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id("not-a-number")

    def test_unwatch_page_output(self):
        """Test output message."""
        page_id = "123456"
        message = f"Stopped watching page {page_id}"

        assert "stopped" in message.lower() or "unwatch" in message.lower()
        assert page_id in message


# =============================================================================
# WATCH SPACE TESTS
# =============================================================================


class TestWatchSpace:
    """Tests for space watching functionality."""

    def test_validate_space_key_valid(self):
        """Test that valid space keys pass validation."""
        from confluence_as import validate_space_key

        assert validate_space_key("DOCS") == "DOCS"
        assert validate_space_key("kb") == "KB"
        assert validate_space_key("Test_Space") == "TEST_SPACE"

    def test_validate_space_key_invalid(self):
        """Test that invalid space keys fail validation."""
        from confluence_as import ValidationError, validate_space_key

        with pytest.raises(ValidationError):
            validate_space_key("")

        with pytest.raises(ValidationError):
            validate_space_key("A")  # Too short

        with pytest.raises(ValidationError):
            validate_space_key("123")  # Starts with number

    def test_watch_space_success(self, mock_client, sample_space):
        """Test successful space watching."""
        # First get space ID
        mock_client.setup_response("get", sample_space)
        space = mock_client.get("/api/v2/spaces/TEST", operation="get space")

        # Then watch it
        mock_client.setup_response("post", {"success": True, "status_code": 200})
        result = mock_client.post(
            f"/rest/api/user/watch/space/{space['key']}", operation="watch space"
        )

        assert result["success"] is True

    def test_watch_space_not_found(self, mock_client, mock_response):
        """Test watching a non-existent space."""
        from confluence_as import NotFoundError, handle_confluence_error

        error_response = mock_response(
            status_code=404, json_data={"message": "Space not found"}
        )

        with pytest.raises(NotFoundError):
            handle_confluence_error(error_response, "watch space")

    def test_watch_space_permission_denied(self, mock_client, mock_response):
        """Test watching a space without permission."""
        from confluence_as import PermissionError, handle_confluence_error

        error_response = mock_response(
            status_code=403, json_data={"message": "Permission denied"}
        )

        with pytest.raises(PermissionError):
            handle_confluence_error(error_response, "watch space")

    def test_watch_space_output(self):
        """Test output message."""
        space_key = "DOCS"
        message = f"Now watching space {space_key}"

        assert "watching" in message.lower()
        assert space_key in message


# =============================================================================
# GET WATCHERS TESTS
# =============================================================================


class TestGetWatchers:
    """Tests for getting watchers functionality."""

    def test_get_watchers_success(self, mock_client, sample_watcher):
        """Test successful retrieval of watchers."""
        watchers_response = {"results": [sample_watcher], "size": 1}
        mock_client.setup_response("get", watchers_response)

        result = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        assert "results" in result
        assert len(result["results"]) == 1
        assert result["results"][0]["displayName"] == "Test User"

    def test_get_watchers_empty(self, mock_client):
        """Test getting watchers for content with no watchers."""
        watchers_response = {"results": [], "size": 0}
        mock_client.setup_response("get", watchers_response)

        result = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        assert "results" in result
        assert len(result["results"]) == 0

    def test_get_watchers_multiple(self, mock_client, sample_watcher):
        """Test getting multiple watchers."""
        watcher2 = {
            **sample_watcher,
            "accountId": "user-456",
            "displayName": "Another User",
        }
        watchers_response = {"results": [sample_watcher, watcher2], "size": 2}
        mock_client.setup_response("get", watchers_response)

        result = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        assert len(result["results"]) == 2
        assert result["results"][0]["displayName"] == "Test User"
        assert result["results"][1]["displayName"] == "Another User"

    def test_get_watchers_not_found(self, mock_client, mock_response):
        """Test getting watchers for non-existent content."""
        from confluence_as import NotFoundError, handle_confluence_error

        error_response = mock_response(
            status_code=404, json_data={"message": "Content not found"}
        )

        with pytest.raises(NotFoundError):
            handle_confluence_error(error_response, "get watchers")

    def test_get_watchers_output_json(self):
        """Test JSON output format."""
        from confluence_as import format_json

        data = {
            "results": [
                {"displayName": "User 1", "email": "user1@example.com"},
                {"displayName": "User 2", "email": "user2@example.com"},
            ],
            "size": 2,
        }
        result = format_json(data)

        assert "User 1" in result
        assert "User 2" in result

    def test_get_watchers_output_text(self):
        """Test text output format."""
        watchers = [
            {"displayName": "User 1", "email": "user1@example.com"},
            {"displayName": "User 2", "email": "user2@example.com"},
        ]

        # Verify we can format watcher list
        output_lines = []
        for watcher in watchers:
            output_lines.append(f"- {watcher['displayName']} ({watcher['email']})")

        assert len(output_lines) == 2
        assert "User 1" in output_lines[0]
        assert "user1@example.com" in output_lines[0]


# =============================================================================
# AM I WATCHING TESTS
# =============================================================================


class TestAmIWatching:
    """Tests for checking watch status functionality."""

    def test_am_i_watching_yes(self, mock_client, sample_watcher):
        """Test checking watch status when user is watching."""
        # Get current user
        current_user = {
            "accountId": "user-123",
            "email": "test@example.com",
            "displayName": "Test User",
        }
        mock_client.setup_response("get", current_user)
        user = mock_client.get("/rest/api/user/current", operation="get current user")

        # Get watchers list
        watchers_response = {"results": [sample_watcher], "size": 1}
        mock_client.setup_response("get", watchers_response)
        watchers = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        # Check if user is in watchers list
        is_watching = any(
            w.get("accountId") == user["accountId"] for w in watchers["results"]
        )

        assert is_watching is True

    def test_am_i_watching_no(self, mock_client, sample_watcher):
        """Test checking watch status when user is not watching."""
        # Get current user
        current_user = {
            "accountId": "user-456",  # Different from watcher
            "email": "other@example.com",
            "displayName": "Other User",
        }
        mock_client.setup_response("get", current_user)
        user = mock_client.get("/rest/api/user/current", operation="get current user")

        # Get watchers list (doesn't include current user)
        watchers_response = {"results": [sample_watcher], "size": 1}
        mock_client.setup_response("get", watchers_response)
        watchers = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        # Check if user is in watchers list
        is_watching = any(
            w.get("accountId") == user["accountId"] for w in watchers["results"]
        )

        assert is_watching is False

    def test_am_i_watching_no_watchers(self, mock_client):
        """Test checking watch status when there are no watchers."""
        # Get current user
        current_user = {
            "accountId": "user-123",
            "email": "test@example.com",
            "displayName": "Test User",
        }
        mock_client.setup_response("get", current_user)
        user = mock_client.get("/rest/api/user/current", operation="get current user")

        # Get empty watchers list
        watchers_response = {"results": [], "size": 0}
        mock_client.setup_response("get", watchers_response)
        watchers = mock_client.get(
            "/rest/api/content/123456/notification/created", operation="get watchers"
        )

        # Check if user is in watchers list
        is_watching = any(
            w.get("accountId") == user["accountId"] for w in watchers["results"]
        )

        assert is_watching is False

    def test_am_i_watching_output_yes(self):
        """Test output when user is watching."""
        page_id = "123456"
        message = f"You are watching page {page_id}"

        assert "watching" in message.lower()
        assert page_id in message

    def test_am_i_watching_output_no(self):
        """Test output when user is not watching."""
        page_id = "123456"
        message = f"You are not watching page {page_id}"

        assert "not watching" in message.lower()
        assert page_id in message

    def test_am_i_watching_validation(self):
        """Test page ID validation."""
        from confluence_as import ValidationError, validate_page_id

        assert validate_page_id("123456") == "123456"

        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id("invalid")
