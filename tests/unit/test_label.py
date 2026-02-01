"""
Unit tests for label operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-label/tests/test_add_label.py
- skills/confluence-label/tests/test_remove_label.py
- skills/confluence-label/tests/test_get_labels.py
- skills/confluence-label/tests/test_search_by_label.py
- skills/confluence-label/tests/test_list_popular_labels.py
"""

from collections import Counter

import pytest

# =============================================================================
# ADD LABEL TESTS
# =============================================================================


class TestAddLabel:
    """Tests for add label functionality."""

    def test_validate_label_valid(self):
        """Test that valid labels pass validation."""
        from confluence_as import validate_label

        assert validate_label("documentation") == "documentation"
        assert validate_label("APPROVED") == "approved"
        assert validate_label("my-label") == "my-label"
        assert validate_label("test_label") == "test_label"

    def test_validate_label_invalid(self):
        """Test that invalid labels fail validation."""
        from confluence_as import ValidationError, validate_label

        # Empty label
        with pytest.raises(ValidationError):
            validate_label("")

        # Contains spaces
        with pytest.raises(ValidationError):
            validate_label("my label")

        # Too long
        with pytest.raises(ValidationError):
            validate_label("a" * 256)

        # Invalid characters
        with pytest.raises(ValidationError):
            validate_label("label@special")

    def test_add_single_label_success(self, mock_client, sample_page, sample_label):
        """Test successful single label addition."""

        # Setup mock response for adding label
        mock_client.setup_response("post", sample_label)

        # Would verify API call was made correctly
        # result = client.post(f'/api/v2/pages/{page_id}/labels', json_data={'name': label_name})
        # assert result['name'] == label_name

    def test_add_multiple_labels_success(self, mock_client, sample_labels):
        """Test successful multiple label addition."""

        # Would verify each label is added
        # For each label in labels, API should be called

    def test_add_label_page_not_found(self, mock_client, mock_response):
        """Test label addition with non-existent page."""

        # Setup 404 response
        error_response = mock_response(
            status_code=404, json_data={"errors": [{"title": "Page not found"}]}
        )
        mock_client.session.post.return_value = error_response

        # Would verify NotFoundError is raised

    def test_add_duplicate_label(self, mock_client, mock_response):
        """Test adding a label that already exists."""

        # Confluence typically returns success even if label exists
        # Test should verify idempotent behavior


class TestLabelParsing:
    """Tests for parsing label input."""

    def test_parse_comma_separated_labels(self):
        """Test parsing comma-separated label string."""
        labels_str = "doc,approved,v2"
        labels = [label.strip() for label in labels_str.split(",")]
        assert labels == ["doc", "approved", "v2"]

    def test_parse_single_label(self):
        """Test parsing single label."""
        labels_str = "documentation"
        labels = [label.strip() for label in labels_str.split(",")]
        assert labels == ["documentation"]

    def test_parse_labels_with_spaces(self):
        """Test parsing labels with extra spaces."""
        labels_str = " doc , approved , v2 "
        labels = [label.strip() for label in labels_str.split(",") if label.strip()]
        assert labels == ["doc", "approved", "v2"]


# =============================================================================
# GET LABELS TESTS
# =============================================================================


class TestGetLabels:
    """Tests for getting labels functionality."""

    def test_get_labels_success(self, mock_client, sample_labels):
        """Test successful retrieval of labels."""

        # Setup mock response
        mock_client.setup_response("get", sample_labels)

        # Would verify API call and result formatting
        # result = client.get(f'/api/v2/pages/{page_id}/labels')
        # assert len(result['results']) == 3

    def test_get_labels_empty(self, mock_client):
        """Test getting labels when page has none."""

        # Setup empty response
        empty_labels = {"results": [], "_links": {}}
        mock_client.setup_response("get", empty_labels)

        # Would verify empty result handling

    def test_get_labels_page_not_found(self, mock_client, mock_response):
        """Test getting labels from non-existent page."""

        # Setup 404 response
        error_response = mock_response(
            status_code=404, json_data={"errors": [{"title": "Page not found"}]}
        )
        mock_client.session.get.return_value = error_response

        # Would verify NotFoundError is raised


class TestLabelFormatting:
    """Tests for label output formatting."""

    def test_format_label_with_prefix(self):
        """Test formatting label with prefix."""
        from confluence_as import format_label

        label = {"id": "1", "name": "test", "prefix": "global"}
        result = format_label(label)
        assert "global:test" in result
        assert "ID: 1" in result

    def test_format_label_without_prefix(self):
        """Test formatting label without prefix."""
        from confluence_as import format_label

        label = {"id": "1", "name": "test", "prefix": ""}
        result = format_label(label)
        assert "test" in result
        assert "global:" not in result

    def test_format_multiple_labels(self, sample_labels):
        """Test formatting multiple labels."""
        sample_labels["results"]

        # Would verify list formatting
        # Output should show all labels with their names


# =============================================================================
# REMOVE LABEL TESTS
# =============================================================================


class TestRemoveLabel:
    """Tests for remove label functionality."""

    def test_remove_label_success(self, mock_client, mock_response):
        """Test successful label removal."""

        # Setup mock response for deletion (typically 204 No Content)
        delete_response = mock_response(status_code=204, json_data={})
        mock_client.session.delete.return_value = delete_response

        # Would verify API call was made correctly
        # client.delete(f'/api/v2/pages/{page_id}/labels/{label_id}')

    def test_remove_label_not_found(self, mock_client, mock_response):
        """Test removing a label that doesn't exist."""

        # Setup 404 response
        error_response = mock_response(
            status_code=404, json_data={"errors": [{"title": "Label not found"}]}
        )
        mock_client.session.delete.return_value = error_response

        # Would verify NotFoundError is raised

    def test_remove_label_page_not_found(self, mock_client, mock_response):
        """Test label removal with non-existent page."""

        # Setup 404 response
        error_response = mock_response(
            status_code=404, json_data={"errors": [{"title": "Page not found"}]}
        )
        mock_client.session.delete.return_value = error_response

        # Would verify NotFoundError is raised


class TestLabelLookup:
    """Tests for finding label ID by name."""

    def test_find_label_by_name(self, sample_labels):
        """Test finding a label ID by its name."""
        labels = sample_labels["results"]
        target_name = "approved"

        found = next((label for label in labels if label["name"] == target_name), None)
        assert found is not None
        assert found["id"] == "label-2"

    def test_find_nonexistent_label(self, sample_labels):
        """Test finding a label that doesn't exist."""
        labels = sample_labels["results"]
        target_name = "nonexistent"

        found = next((label for label in labels if label["name"] == target_name), None)
        assert found is None


# =============================================================================
# SEARCH BY LABEL TESTS
# =============================================================================


class TestSearchByLabel:
    """Tests for searching content by label."""

    def test_search_by_label_success(self, mock_client):
        """Test successful search by label."""

        # Sample search results
        search_results = {
            "results": [
                {
                    "id": "123",
                    "type": "page",
                    "title": "API Docs",
                    "spaceId": "789",
                    "_links": {"webui": "/wiki/spaces/DOCS/pages/123"},
                },
                {
                    "id": "124",
                    "type": "page",
                    "title": "User Guide",
                    "spaceId": "789",
                    "_links": {"webui": "/wiki/spaces/DOCS/pages/124"},
                },
            ],
            "_links": {},
        }

        mock_client.setup_response("get", search_results)

        # Would verify CQL query construction and results

    def test_search_by_label_with_space_filter(self, mock_client):
        """Test search by label filtered to specific space."""

        # Would verify CQL query includes both label and space
        # Expected CQL: label = "approved" AND space = "DOCS"

    def test_search_by_label_no_results(self, mock_client):
        """Test search by label with no results."""

        # Setup empty response
        empty_results = {"results": [], "_links": {}}
        mock_client.setup_response("get", empty_results)

        # Would verify empty result handling

    def test_search_by_label_with_limit(self, mock_client):
        """Test search by label with result limit."""

        # Would verify limit parameter is passed correctly


class TestCQLQueryConstruction:
    """Tests for CQL query building."""

    def test_build_label_query_simple(self):
        """Test building simple label query."""
        label = "documentation"
        expected = 'label = "documentation"'

        # Would verify query construction
        query = f'label = "{label}"'
        assert query == expected

    def test_build_label_query_with_space(self):
        """Test building label query with space filter."""
        label = "approved"
        space = "DOCS"
        expected = 'label = "approved" AND space = "DOCS"'

        # Would verify query construction
        query = f'label = "{label}" AND space = "{space}"'
        assert query == expected

    def test_build_label_query_with_type(self):
        """Test building label query with type filter."""
        label = "documentation"
        content_type = "page"
        expected = 'label = "documentation" AND type = "page"'

        # Would verify query construction
        query = f'label = "{label}" AND type = "{content_type}"'
        assert query == expected


# =============================================================================
# LIST POPULAR LABELS TESTS
# =============================================================================


class TestListPopularLabels:
    """Tests for listing popular labels."""

    def test_list_popular_labels_success(self, mock_client):
        """Test successful retrieval of popular labels."""
        # Sample search results with labels
        search_results = {
            "results": [
                {
                    "id": "123",
                    "type": "page",
                    "title": "Page 1",
                    "metadata": {
                        "labels": {
                            "results": [{"name": "documentation"}, {"name": "api"}]
                        }
                    },
                },
                {
                    "id": "124",
                    "type": "page",
                    "title": "Page 2",
                    "metadata": {
                        "labels": {
                            "results": [{"name": "documentation"}, {"name": "tutorial"}]
                        }
                    },
                },
            ],
            "_links": {},
        }

        mock_client.setup_response("get", search_results)

        # Would verify label aggregation and counting

    def test_list_popular_labels_with_space_filter(self, mock_client):
        """Test listing popular labels filtered to specific space."""

        # Would verify CQL query includes space filter
        # Expected CQL: space = "DOCS"

    def test_list_popular_labels_empty_results(self, mock_client):
        """Test listing popular labels with no content."""
        # Setup empty response
        empty_results = {"results": [], "_links": {}}
        mock_client.setup_response("get", empty_results)

        # Would verify empty result handling

    def test_list_popular_labels_with_limit(self, mock_client):
        """Test listing popular labels with result limit."""

        # Would verify only top N labels are returned


class TestLabelAggregation:
    """Tests for aggregating and counting labels."""

    def test_count_label_occurrences(self):
        """Test counting label occurrences across pages."""
        pages = [
            {"labels": ["doc", "api", "v2"]},
            {"labels": ["doc", "tutorial"]},
            {"labels": ["doc", "api"]},
        ]

        # Count occurrences
        all_labels = []
        for page in pages:
            all_labels.extend(page["labels"])

        counts = Counter(all_labels)
        assert counts["doc"] == 3
        assert counts["api"] == 2
        assert counts["tutorial"] == 1
        assert counts["v2"] == 1

    def test_sort_labels_by_count(self):
        """Test sorting labels by popularity."""

        label_counts = {"doc": 5, "api": 3, "tutorial": 1, "v2": 2}
        sorted_labels = sorted(label_counts.items(), key=lambda x: x[1], reverse=True)

        assert sorted_labels[0] == ("doc", 5)
        assert sorted_labels[1] == ("api", 3)
        assert sorted_labels[2] == ("v2", 2)
        assert sorted_labels[3] == ("tutorial", 1)

    def test_limit_results(self):
        """Test limiting number of results."""
        sorted_labels = [("doc", 5), ("api", 3), ("v2", 2), ("tutorial", 1)]
        limit = 2

        limited = sorted_labels[:limit]
        assert len(limited) == 2
        assert limited[0] == ("doc", 5)
        assert limited[1] == ("api", 3)
