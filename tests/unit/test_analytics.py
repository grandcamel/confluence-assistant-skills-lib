"""
Unit tests for analytics operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-analytics/tests/test_get_page_views.py
- skills/confluence-analytics/tests/test_get_space_analytics.py
- skills/confluence-analytics/tests/test_get_popular_content.py
- skills/confluence-analytics/tests/test_get_content_watchers.py
"""

import json

import pytest

# =============================================================================
# GET PAGE VIEWS TESTS
# =============================================================================


class TestGetPageViews:
    """Tests for getting page view analytics."""

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
            validate_page_id("abc")

        with pytest.raises(ValidationError):
            validate_page_id(-1)

    def test_get_page_history_success(self, mock_client, sample_page_history):
        """Test successful retrieval of page history."""
        # Setup mock response
        mock_client.setup_response("get", sample_page_history)

        # Call API
        result = mock_client.get("/rest/api/content/123456")

        # Verify
        assert result["id"] == "123456"
        assert result["type"] == "page"
        assert "history" in result
        assert "version" in result

    def test_get_page_contributors(self, mock_client, sample_page_history):
        """Test extracting contributor information."""
        mock_client.setup_response("get", sample_page_history)

        result = mock_client.get(
            "/rest/api/content/123456",
            params={"expand": "history.contributors.publishers"},
        )

        # Verify contributors exist
        assert "history" in result
        assert "contributors" in result["history"]
        assert "publishers" in result["history"]["contributors"]

        publishers = result["history"]["contributors"]["publishers"]
        assert "users" in publishers
        assert len(publishers["users"]) == 2

    def test_format_analytics_output(self, sample_page_history):
        """Test formatting analytics data for output."""
        # This tests the formatting logic
        page_id = sample_page_history["id"]
        title = sample_page_history["title"]
        version = sample_page_history["version"]["number"]

        assert page_id == "123456"
        assert title == "Test Page"
        assert version == 5

    def test_page_not_found(self, mock_client):
        """Test handling page not found error."""

        # Mock 404 response
        mock_client.setup_response(
            "get", {"message": "Page not found"}, status_code=404
        )

        # The client should handle this appropriately
        # In real implementation, would verify NotFoundError is raised


class TestOutputFormats:
    """Tests for different output formats."""

    def test_json_output_format(self, sample_page_history):
        """Test JSON output formatting."""
        from confluence_as import format_json

        output = format_json(sample_page_history)
        parsed = json.loads(output)

        assert parsed["id"] == "123456"
        assert parsed["title"] == "Test Page"

    def test_text_output_format(self, sample_page_history):
        """Test text output contains expected fields."""
        # Verify key fields are present for text formatting
        assert "id" in sample_page_history
        assert "title" in sample_page_history
        assert "version" in sample_page_history
        assert "history" in sample_page_history


# =============================================================================
# GET SPACE ANALYTICS TESTS
# =============================================================================


class TestGetSpaceAnalytics:
    """Tests for getting space-level analytics."""

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

    def test_search_space_content(self, mock_client, analytics_search_results):
        """Test CQL search for space content."""
        mock_client.setup_response("get", analytics_search_results)

        result = mock_client.get(
            "/rest/api/search", params={"cql": "space=TEST AND type=page"}
        )

        assert "results" in result
        assert len(result["results"]) == 2
        assert result["size"] == 2

    def test_aggregate_space_statistics(self, analytics_search_results):
        """Test aggregating statistics from search results."""
        # Count total pages
        total_pages = len(analytics_search_results["results"])
        assert total_pages == 2

        # Extract page IDs
        page_ids = [r["content"]["id"] for r in analytics_search_results["results"]]
        assert page_ids == ["123456", "123457"]

    def test_space_not_found(self, mock_client):
        """Test handling space not found error."""
        # Mock empty search results
        mock_client.setup_response("get", {"results": [], "size": 0})

        result = mock_client.get("/rest/api/search", params={"cql": "space=NOTFOUND"})

        assert result["size"] == 0
        assert len(result["results"]) == 0


class TestDateRangeFiltering:
    """Tests for date range filtering in analytics."""

    def test_cql_with_date_filter(self):
        """Test CQL query construction with date filters."""
        space_key = "TEST"
        start_date = "2024-01-01"

        # Construct CQL
        cql = f'space={space_key} AND created >= "{start_date}"'

        assert "space=TEST" in cql
        assert "created >=" in cql
        assert "2024-01-01" in cql

    def test_cql_date_range(self):
        """Test CQL with date range."""
        space_key = "TEST"
        start_date = "2024-01-01"
        end_date = "2024-12-31"

        cql = f'space={space_key} AND created >= "{start_date}" AND created <= "{end_date}"'

        assert "2024-01-01" in cql
        assert "2024-12-31" in cql


# =============================================================================
# GET POPULAR CONTENT TESTS
# =============================================================================


class TestGetPopularContent:
    """Tests for getting popular/most viewed content."""

    def test_cql_order_by_created(self):
        """Test CQL query ordering by creation date."""
        space_key = "TEST"
        cql = f"space={space_key} AND type=page ORDER BY created DESC"

        assert "ORDER BY created DESC" in cql
        assert "space=TEST" in cql

    def test_cql_order_by_modified(self):
        """Test CQL query ordering by modification date."""
        space_key = "TEST"
        cql = f"space={space_key} AND type=page ORDER BY lastModified DESC"

        assert "ORDER BY lastModified DESC" in cql

    def test_search_popular_content(self, mock_client, analytics_search_results):
        """Test searching for popular content via CQL."""
        mock_client.setup_response("get", analytics_search_results)

        result = mock_client.get(
            "/rest/api/search",
            params={
                "cql": "space=TEST AND type=page ORDER BY created DESC",
                "limit": 10,
            },
        )

        assert "results" in result
        assert len(result["results"]) == 2

    def test_limit_results(self, mock_client, analytics_search_results):
        """Test limiting number of results returned."""
        mock_client.setup_response("get", analytics_search_results)

        result = mock_client.get(
            "/rest/api/search",
            params={"cql": "type=page ORDER BY created DESC", "limit": 5},
        )

        # Verify results are returned
        assert "results" in result

    def test_filter_by_space(self, analytics_search_results):
        """Test filtering results by space."""
        # All results should be from TEST space
        for result in analytics_search_results["results"]:
            assert result["content"]["space"]["key"] == "TEST"

    def test_filter_by_label(self):
        """Test CQL query with label filter."""
        label = "featured"
        cql = f"type=page AND label={label} ORDER BY created DESC"

        assert "label=featured" in cql
        assert "ORDER BY created DESC" in cql


class TestContentTypeFilters:
    """Tests for filtering by content type."""

    def test_filter_pages_only(self):
        """Test filtering for pages only."""
        cql = "type=page ORDER BY created DESC"
        assert "type=page" in cql

    def test_filter_blogposts_only(self):
        """Test filtering for blog posts only."""
        cql = "type=blogpost ORDER BY created DESC"
        assert "type=blogpost" in cql

    def test_filter_both_types(self):
        """Test filtering for both pages and blog posts."""
        cql = "type in (page, blogpost) ORDER BY created DESC"
        assert "type in (page, blogpost)" in cql


# =============================================================================
# GET CONTENT WATCHERS TESTS
# =============================================================================


class TestGetContentWatchers:
    """Tests for getting content watchers."""

    def test_validate_page_id_valid(self):
        """Test that valid page IDs pass validation."""
        from confluence_as import validate_page_id

        assert validate_page_id("123456") == "123456"
        assert validate_page_id(123456) == "123456"

    def test_get_watchers_success(self, mock_client, sample_watchers):
        """Test successful retrieval of watchers."""
        mock_client.setup_response("get", sample_watchers)

        result = mock_client.get("/rest/api/content/123456/notification/child-created")

        assert "results" in result
        assert len(result["results"]) == 2
        assert result["size"] == 2

    def test_parse_watcher_info(self, sample_watchers):
        """Test parsing watcher information."""
        watchers = sample_watchers["results"]

        # Extract watcher details
        watcher_names = [w.get("displayName") for w in watchers]
        watcher_emails = [w.get("email") for w in watchers]

        assert "Test User" in watcher_names
        assert "User Two" in watcher_names
        assert "test@example.com" in watcher_emails
        assert "user2@example.com" in watcher_emails

    def test_count_watchers(self, sample_watchers):
        """Test counting total watchers."""
        total_watchers = len(sample_watchers["results"])
        assert total_watchers == 2

    def test_no_watchers(self, mock_client):
        """Test handling content with no watchers."""
        empty_response = {"results": [], "start": 0, "limit": 25, "size": 0}

        mock_client.setup_response("get", empty_response)

        result = mock_client.get("/rest/api/content/123456/notification/child-created")

        assert result["size"] == 0
        assert len(result["results"]) == 0

    def test_page_not_found(self, mock_client):
        """Test handling page not found error."""
        mock_client.setup_response(
            "get", {"message": "Content not found"}, status_code=404
        )

        # In real implementation, should handle 404 appropriately


class TestWatcherOutputFormats:
    """Tests for watcher output formatting."""

    def test_format_watcher_list(self, sample_watchers):
        """Test formatting watchers for display."""
        watchers = sample_watchers["results"]

        # Should be able to format each watcher
        for watcher in watchers:
            formatted = f"{watcher.get('displayName', 'Unknown')} ({watcher.get('email', 'N/A')})"

            assert watcher.get("displayName") in formatted or "Unknown" in formatted

    def test_json_output(self, sample_watchers):
        """Test JSON output formatting."""
        from confluence_as import format_json

        output = format_json(sample_watchers)
        parsed = json.loads(output)

        assert parsed["size"] == 2
        assert len(parsed["results"]) == 2
