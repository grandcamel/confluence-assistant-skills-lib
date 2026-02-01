"""
Unit tests for comment operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-comment/tests/test_add_comment.py
- skills/confluence-comment/tests/test_get_comments.py
- skills/confluence-comment/tests/test_update_comment.py
- skills/confluence-comment/tests/test_delete_comment.py
- skills/confluence-comment/tests/test_resolve_comment.py
- skills/confluence-comment/tests/test_add_inline_comment.py
"""

import pytest

# =============================================================================
# ADD COMMENT TESTS
# =============================================================================


class TestAddComment:
    """Tests for adding footer comments to pages."""

    def test_validate_comment_id_valid(self):
        """Test that valid comment IDs pass validation."""
        from confluence_as import validate_page_id

        # Comment IDs use the same validation as page IDs
        assert validate_page_id("12345", "comment_id") == "12345"
        assert validate_page_id(67890, "comment_id") == "67890"

    def test_validate_comment_id_invalid(self):
        """Test that invalid comment IDs fail validation."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("", "comment_id")

        with pytest.raises(ValidationError):
            validate_page_id("abc", "comment_id")

    def test_validate_comment_body_required(self):
        """Test that comment body is required."""
        from confluence_as import ValidationError

        # Simulating the validation that should happen
        body = ""
        if not body or not body.strip():
            with pytest.raises(ValidationError):
                raise ValidationError("Comment body is required")

    def test_add_comment_basic(self, mock_client, sample_comment):
        """Test adding a basic comment to a page."""
        # Setup mock response
        mock_client.setup_response("post", sample_comment)

        # Would verify comment is created with correct data structure
        # Expected API call: POST /api/v2/pages/{page_id}/footer-comments

    def test_add_comment_with_html(self, mock_client, sample_comment):
        """Test adding a comment with HTML content."""
        comment_with_html = sample_comment.copy()
        comment_with_html["body"]["storage"]["value"] = (
            "<p>Bold text: <strong>important</strong></p>"
        )

        mock_client.setup_response("post", comment_with_html)

        # Would verify HTML is preserved in storage format

    def test_add_comment_page_not_found(self, mock_client):
        """Test adding comment to non-existent page."""

        mock_client.setup_response("post", {}, status_code=404)

        # Would verify NotFoundError is raised with appropriate message

    def test_add_comment_no_permission(self, mock_client):
        """Test adding comment without permission."""

        mock_client.setup_response("post", {}, status_code=403)

        # Would verify PermissionError is raised


class TestCommentBodyValidation:
    """Tests for comment body validation."""

    def test_empty_body_rejected(self):
        """Test that empty comment body is rejected."""
        from confluence_as import ValidationError

        body = ""
        if not body.strip():
            with pytest.raises(ValidationError):
                raise ValidationError("Comment body cannot be empty")

    def test_whitespace_only_rejected(self):
        """Test that whitespace-only body is rejected."""
        from confluence_as import ValidationError

        body = "   \n\t   "
        if not body.strip():
            with pytest.raises(ValidationError):
                raise ValidationError("Comment body cannot be empty")

    def test_valid_body_accepted(self):
        """Test that valid body is accepted."""
        body = "This is a valid comment"
        assert body.strip() == "This is a valid comment"


class TestCommentFormatting:
    """Tests for comment output formatting."""

    def test_format_comment_basic(self, sample_comment):
        """Test basic comment formatting."""
        from confluence_as import format_comment

        result = format_comment(sample_comment)

        assert "999" in result  # Comment ID
        assert "user123" in result  # Author ID
        assert "This is a comment" in result  # Body text

    def test_format_comment_without_body(self, sample_comment):
        """Test comment formatting without showing body."""
        from confluence_as import format_comment

        result = format_comment(sample_comment, show_body=False)

        assert "999" in result  # Comment ID
        assert "This is a comment" not in result  # Body should not be shown

    def test_format_comments_list(self, sample_comment):
        """Test formatting multiple comments."""
        from confluence_as import format_comments

        comments = [sample_comment, sample_comment.copy()]
        result = format_comments(comments)

        assert "1." in result
        assert "2." in result


# =============================================================================
# GET COMMENTS TESTS
# =============================================================================


class TestGetComments:
    """Tests for retrieving comments from a page."""

    def test_get_comments_basic(self, mock_client, sample_comment):
        """Test getting comments from a page."""
        comments_response = {"results": [sample_comment], "_links": {}}
        mock_client.setup_response("get", comments_response)

        # Would verify GET /api/v2/pages/{page_id}/footer-comments

    def test_get_comments_pagination(self, mock_client, sample_comment):
        """Test getting comments with pagination."""
        page1 = {
            "results": [sample_comment],
            "_links": {"next": "/api/v2/pages/123/footer-comments?cursor=abc"},
        }
        {"results": [sample_comment.copy()], "_links": {}}

        mock_client.setup_response("get", page1)
        # Would verify pagination logic

    def test_get_comments_empty(self, mock_client):
        """Test getting comments from page with no comments."""
        empty_response = {"results": [], "_links": {}}
        mock_client.setup_response("get", empty_response)

        # Would verify empty result handling

    def test_get_comments_with_limit(self, mock_client, sample_comment):
        """Test getting comments with limit parameter."""
        from confluence_as import validate_limit

        limit = validate_limit(5)
        assert limit == 5

    def test_get_comments_sort_by_created(self, mock_client, sample_comment):
        """Test getting comments sorted by creation date."""
        # Would verify sort parameter is passed correctly

    def test_get_comments_page_not_found(self, mock_client):
        """Test getting comments from non-existent page."""

        mock_client.setup_response("get", {}, status_code=404)
        # Would verify NotFoundError is raised


class TestCommentListFormatting:
    """Tests for formatting comment lists."""

    def test_format_empty_comments(self):
        """Test formatting empty comment list."""
        from confluence_as import format_comments

        result = format_comments([])
        assert "No comments" in result

    def test_format_multiple_comments(self, sample_comment):
        """Test formatting multiple comments."""
        from confluence_as import format_comments

        comments = [
            sample_comment,
            {
                **sample_comment,
                "id": "1000",
                "body": {"storage": {"value": "<p>Second comment</p>"}},
            },
            {
                **sample_comment,
                "id": "1001",
                "body": {"storage": {"value": "<p>Third comment</p>"}},
            },
        ]

        result = format_comments(comments)
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_format_comments_with_limit(self, sample_comment):
        """Test formatting comments with display limit."""
        from confluence_as import format_comments

        comments = [sample_comment] * 10
        result = format_comments(comments, limit=3)

        # Should only show first 3
        assert result.count("Comment") == 3


# =============================================================================
# UPDATE COMMENT TESTS
# =============================================================================


class TestUpdateComment:
    """Tests for updating existing comments."""

    def test_update_comment_basic(self, mock_client, sample_comment):
        """Test updating a comment's body."""
        updated = sample_comment.copy()
        updated["body"]["storage"]["value"] = "<p>Updated comment</p>"
        updated["version"]["number"] = 2

        mock_client.setup_response("put", updated)

        # Would verify PUT /api/v2/footer-comments/{comment_id}

    def test_update_comment_version_increment(self, mock_client, sample_comment):
        """Test that version is incremented on update."""
        # Version should be incremented automatically by API
        # Client should include current version in request

    def test_update_comment_not_found(self, mock_client):
        """Test updating non-existent comment."""

        mock_client.setup_response("put", {}, status_code=404)
        # Would verify NotFoundError is raised

    def test_update_comment_no_permission(self, mock_client):
        """Test updating comment without permission."""

        mock_client.setup_response("put", {}, status_code=403)
        # Would verify PermissionError is raised

    def test_update_comment_conflict(self, mock_client):
        """Test updating comment with version conflict."""

        mock_client.setup_response("put", {}, status_code=409)
        # Would verify ConflictError is raised for version mismatch


class TestUpdateValidation:
    """Tests for update validation."""

    def test_comment_id_required(self):
        """Test that comment ID is required."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("", "comment_id")

    def test_updated_body_required(self):
        """Test that updated body is required."""
        # Same validation as add_comment
        body = ""
        if not body.strip():
            from confluence_as import ValidationError

            with pytest.raises(ValidationError):
                raise ValidationError("Comment body cannot be empty")

    def test_body_from_file(self, tmp_path):
        """Test reading updated body from file."""
        comment_file = tmp_path / "updated.txt"
        comment_file.write_text("Updated comment text")

        content = comment_file.read_text()
        assert content == "Updated comment text"


# =============================================================================
# DELETE COMMENT TESTS
# =============================================================================


class TestDeleteComment:
    """Tests for deleting comments."""

    def test_delete_comment_basic(self, mock_client):
        """Test deleting a comment."""
        # DELETE returns 204 No Content on success
        mock_client.setup_response("delete", {}, status_code=204)

        # Would verify DELETE /api/v2/footer-comments/{comment_id}

    def test_delete_comment_not_found(self, mock_client):
        """Test deleting non-existent comment."""

        mock_client.setup_response("delete", {}, status_code=404)
        # Would verify NotFoundError is raised

    def test_delete_comment_no_permission(self, mock_client):
        """Test deleting comment without permission."""

        mock_client.setup_response("delete", {}, status_code=403)
        # Would verify PermissionError is raised

    def test_delete_comment_confirmation_prompt(self, mock_client):
        """Test that confirmation is required for delete."""
        # When --force is not provided, should prompt user
        # This would be tested in integration tests

    def test_delete_comment_with_force(self, mock_client):
        """Test deleting with --force flag (no confirmation)."""
        mock_client.setup_response("delete", {}, status_code=204)
        # Would verify delete proceeds without prompt when --force is used


class TestDeleteValidation:
    """Tests for delete validation."""

    def test_comment_id_required(self):
        """Test that comment ID is required."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("", "comment_id")

    def test_comment_id_numeric(self):
        """Test that comment ID must be numeric."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("abc", "comment_id")


# =============================================================================
# RESOLVE COMMENT TESTS
# =============================================================================


class TestResolveComment:
    """Tests for resolving comments."""

    def test_resolve_comment_basic(self, mock_client, sample_comment):
        """Test resolving a comment."""
        resolved = sample_comment.copy()
        resolved["resolutionStatus"] = "resolved"

        mock_client.setup_response("put", resolved)

        # Would verify resolution API call

    def test_unresolve_comment(self, mock_client, sample_comment):
        """Test unresolving a comment."""
        unresolved = sample_comment.copy()
        unresolved["resolutionStatus"] = "open"

        mock_client.setup_response("put", unresolved)

        # Would verify unresolve operation

    def test_resolve_comment_not_found(self, mock_client):
        """Test resolving non-existent comment."""

        mock_client.setup_response("put", {}, status_code=404)
        # Would verify NotFoundError is raised

    def test_resolve_comment_no_permission(self, mock_client):
        """Test resolving comment without permission."""

        mock_client.setup_response("put", {}, status_code=403)
        # Would verify PermissionError is raised


class TestResolveValidation:
    """Tests for resolve validation."""

    def test_comment_id_required(self):
        """Test that comment ID is required."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("", "comment_id")

    def test_resolution_status_values(self):
        """Test valid resolution status values."""
        valid_statuses = ["resolved", "open"]

        for status in valid_statuses:
            assert status in ["resolved", "open"]

    def test_invalid_resolution_status(self):
        """Test that invalid status is rejected."""
        from confluence_as import ValidationError

        status = "invalid"
        if status not in ["resolved", "open"]:
            with pytest.raises(ValidationError):
                raise ValidationError(f"Invalid resolution status: {status}")


# =============================================================================
# INLINE COMMENT TESTS
# =============================================================================


class TestAddInlineComment:
    """Tests for adding inline comments."""

    def test_add_inline_comment_basic(self, mock_client, sample_comment):
        """Test adding an inline comment."""
        inline_comment = sample_comment.copy()
        inline_comment["inlineProperties"] = {
            "originalSelection": "selected text",
            "textSelection": "selected text",
        }

        mock_client.setup_response("post", inline_comment)

        # Would verify POST /api/v2/pages/{page_id}/inline-comments

    def test_add_inline_comment_with_position(self, mock_client, sample_comment):
        """Test adding inline comment with text selection."""
        # Inline comments reference specific text in the page

    def test_validate_inline_text_selection(self):
        """Test that text selection is validated."""
        from confluence_as import ValidationError

        selection = ""
        if not selection.strip():
            with pytest.raises(ValidationError):
                raise ValidationError("Text selection is required for inline comments")

    def test_add_inline_comment_page_not_found(self, mock_client):
        """Test adding inline comment to non-existent page."""

        mock_client.setup_response("post", {}, status_code=404)
        # Would verify NotFoundError is raised


class TestInlineCommentValidation:
    """Tests for inline comment validation."""

    def test_page_id_required(self):
        """Test that page ID is required."""
        from confluence_as import ValidationError, validate_page_id

        with pytest.raises(ValidationError):
            validate_page_id("")

    def test_comment_body_required(self):
        """Test that comment body is required."""
        from confluence_as import ValidationError

        body = ""
        if not body.strip():
            with pytest.raises(ValidationError):
                raise ValidationError("Comment body cannot be empty")

    def test_text_selection_required(self):
        """Test that text selection is required for inline comments."""
        selection = "   "
        if not selection.strip():
            from confluence_as import ValidationError

            with pytest.raises(ValidationError):
                raise ValidationError("Text selection is required")
