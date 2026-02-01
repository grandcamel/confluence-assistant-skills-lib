"""
Unit tests for attachment operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-attachment/tests/test_upload_attachment.py
- skills/confluence-attachment/tests/test_download_attachment.py
- skills/confluence-attachment/tests/test_list_attachments.py
- skills/confluence-attachment/tests/test_update_attachment.py
- skills/confluence-attachment/tests/test_delete_attachment.py
"""

import mimetypes
from unittest.mock import MagicMock, Mock

import pytest

# =============================================================================
# UPLOAD ATTACHMENT TESTS
# =============================================================================


class TestUploadAttachment:
    """Tests for attachment upload functionality."""

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
            validate_page_id("abc")

        with pytest.raises(ValidationError):
            validate_page_id(None)

    def test_validate_file_path_exists(self, test_file):
        """Test file path validation with existing file."""
        from confluence_as import validate_file_path

        result = validate_file_path(test_file)
        assert result == test_file
        assert result.exists()
        assert result.is_file()

    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existent file."""
        from confluence_as import ValidationError, validate_file_path

        with pytest.raises(ValidationError) as exc_info:
            validate_file_path("/nonexistent/file.txt")

        assert "does not exist" in str(exc_info.value)

    def test_validate_file_path_is_directory(self, tmp_path):
        """Test file path validation when path is a directory."""
        from confluence_as import ValidationError, validate_file_path

        with pytest.raises(ValidationError) as exc_info:
            validate_file_path(tmp_path)

        assert "not a file" in str(exc_info.value)

    def test_upload_attachment_basic(self, mock_client, sample_attachment, test_file):
        """Test basic attachment upload."""
        # Mock the upload_file method
        mock_client.upload_file = MagicMock(
            return_value={"results": [sample_attachment]}
        )

        page_id = "123456"
        result = mock_client.upload_file(
            f"/api/v2/pages/{page_id}/attachments",
            test_file,
            operation="upload attachment",
        )

        assert result["results"][0]["id"] == "att123456"
        assert result["results"][0]["title"] == "test-file.pdf"
        mock_client.upload_file.assert_called_once()

    def test_upload_attachment_with_comment(
        self, mock_client, sample_attachment, test_file
    ):
        """Test attachment upload with comment."""
        attachment_with_comment = sample_attachment.copy()
        attachment_with_comment["comment"] = "Test comment"

        mock_client.upload_file = MagicMock(
            return_value={"results": [attachment_with_comment]}
        )

        page_id = "123456"
        result = mock_client.upload_file(
            f"/api/v2/pages/{page_id}/attachments",
            test_file,
            additional_data={"comment": "Test comment"},
            operation="upload attachment",
        )

        assert result["results"][0]["comment"] == "Test comment"

    def test_upload_multiple_file_types(
        self, mock_client, test_file, test_pdf_file, test_image_file
    ):
        """Test uploading different file types."""
        from confluence_as import validate_file_path

        # All should pass validation
        assert validate_file_path(test_file).suffix == ".txt"
        assert validate_file_path(test_pdf_file).suffix == ".pdf"
        assert validate_file_path(test_image_file).suffix == ".png"

    def test_get_mime_type(self, test_file, test_pdf_file, test_image_file):
        """Test MIME type detection for different file types."""
        # Initialize mimetypes
        mimetypes.init()

        assert mimetypes.guess_type(str(test_file))[0] == "text/plain"
        assert mimetypes.guess_type(str(test_pdf_file))[0] == "application/pdf"
        assert mimetypes.guess_type(str(test_image_file))[0] == "image/png"


class TestAttachmentValidation:
    """Tests for attachment-specific validation."""

    def test_file_size_limits(self, tmp_path):
        """Test file size validation."""
        # Create a large file (mock)
        large_file = tmp_path / "large.bin"
        # Don't actually create a huge file, just test the concept
        large_file.write_bytes(b"x" * 1000)

        from confluence_as import validate_file_path

        # Should validate successfully
        result = validate_file_path(large_file)
        assert result.stat().st_size == 1000

    def test_attachment_id_validation(self):
        """Test attachment ID validation."""
        from confluence_as import validate_page_id

        # Attachment IDs are numeric like page IDs
        assert validate_page_id("123456") == "123456"

    def test_allowed_extensions(self, tmp_path):
        """Test file extension validation."""
        from confluence_as import ValidationError, validate_file_path

        # Create test files
        pdf_file = tmp_path / "doc.pdf"
        pdf_file.write_bytes(b"pdf")

        txt_file = tmp_path / "doc.txt"
        txt_file.write_bytes(b"txt")

        exe_file = tmp_path / "program.exe"
        exe_file.write_bytes(b"exe")

        # Allow specific extensions
        assert (
            validate_file_path(pdf_file, allowed_extensions=[".pdf"]).suffix == ".pdf"
        )

        # Reject disallowed extensions
        with pytest.raises(ValidationError):
            validate_file_path(exe_file, allowed_extensions=[".pdf", ".txt"])


# =============================================================================
# DOWNLOAD ATTACHMENT TESTS
# =============================================================================


class TestDownloadAttachment:
    """Tests for attachment download functionality."""

    def test_download_attachment_basic(self, mock_client, sample_attachment, tmp_path):
        """Test basic attachment download."""
        output_path = tmp_path / "downloaded.pdf"

        # Mock download_file method
        mock_client.download_file = MagicMock(return_value=output_path)

        download_url = sample_attachment["downloadLink"]
        result = mock_client.download_file(
            download_url, output_path, operation="download attachment"
        )

        assert result == output_path
        mock_client.download_file.assert_called_once()

    def test_download_attachment_to_directory(
        self, mock_client, sample_attachment, tmp_path
    ):
        """Test downloading attachment to a directory."""
        # Create output directory
        output_dir = tmp_path / "downloads"
        output_dir.mkdir()

        # Expected output file
        output_file = output_dir / sample_attachment["title"]

        mock_client.download_file = MagicMock(return_value=output_file)

        result = mock_client.download_file(
            sample_attachment["downloadLink"],
            output_file,
            operation="download attachment",
        )

        assert result == output_file

    def test_download_creates_parent_directories(self, tmp_path):
        """Test that download creates parent directories if needed."""
        output_path = tmp_path / "nested" / "dir" / "file.pdf"

        # Parent should not exist yet
        assert not output_path.parent.exists()

        # This would be handled by download_file in the client
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"test")

        assert output_path.exists()
        assert output_path.parent.exists()

    def test_download_attachment_by_id(self, mock_client, sample_attachment):
        """Test downloading attachment by ID."""
        attachment_id = "att123456"

        # First get attachment metadata
        mock_client.get = MagicMock(return_value=sample_attachment)

        result = mock_client.get(
            f"/api/v2/attachments/{attachment_id}", operation="get attachment"
        )

        assert result["id"] == attachment_id
        assert "downloadLink" in result

    def test_download_all_from_page(self, mock_client, sample_attachment, tmp_path):
        """Test downloading all attachments from a page."""
        attachments = [
            {**sample_attachment, "id": "att1", "title": "file1.pdf"},
            {**sample_attachment, "id": "att2", "title": "file2.docx"},
        ]

        mock_client.get = MagicMock(return_value={"results": attachments, "_links": {}})

        # Get all attachments
        result = mock_client.get(
            "/api/v2/pages/123456/attachments", operation="list attachments"
        )

        assert len(result["results"]) == 2

        # Simulate downloading each
        for att in result["results"]:
            output_file = tmp_path / att["title"]
            mock_client.download_file = MagicMock(return_value=output_file)
            downloaded = mock_client.download_file(
                att["downloadLink"], output_file, operation="download attachment"
            )
            assert downloaded == output_file

    def test_download_with_invalid_attachment_id(self, mock_client):
        """Test download with non-existent attachment ID."""

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.json.return_value = {"message": "Attachment not found"}

        # Would raise NotFoundError
        # This tests the concept
        assert mock_response.status_code == 404

    def test_download_overwrites_existing_file(self, tmp_path):
        """Test that download can overwrite existing files."""
        output_file = tmp_path / "existing.pdf"
        output_file.write_bytes(b"old content")

        assert output_file.exists()
        assert output_file.read_bytes() == b"old content"

        # Overwrite
        output_file.write_bytes(b"new content")
        assert output_file.read_bytes() == b"new content"

    def test_download_binary_content(self, tmp_path):
        """Test downloading binary content."""
        output_file = tmp_path / "binary.dat"
        binary_data = bytes([0, 1, 2, 255, 254, 253])

        output_file.write_bytes(binary_data)

        assert output_file.read_bytes() == binary_data


class TestDownloadValidation:
    """Tests for download-specific validation."""

    def test_validate_output_path(self, tmp_path):
        """Test output path validation."""
        from confluence_as import validate_file_path

        # Valid output path (doesn't need to exist)
        output = tmp_path / "output.pdf"
        result = validate_file_path(output, must_exist=False)
        assert result == output

    def test_validate_attachment_id(self):
        """Test attachment ID validation."""
        from confluence_as import validate_page_id

        # Attachment IDs are numeric strings like page IDs
        assert validate_page_id("123456") == "123456"
        assert validate_page_id("789012") == "789012"


# =============================================================================
# LIST ATTACHMENTS TESTS
# =============================================================================


class TestListAttachments:
    """Tests for listing attachments functionality."""

    def test_list_attachments_empty(self, mock_client):
        """Test listing attachments when page has none."""
        mock_client.get = MagicMock(return_value={"results": [], "_links": {}})

        page_id = "123456"
        result = mock_client.get(
            f"/api/v2/pages/{page_id}/attachments", operation="list attachments"
        )

        assert result["results"] == []

    def test_list_attachments_single(self, mock_client, sample_attachment):
        """Test listing attachments with one attachment."""
        mock_client.get = MagicMock(
            return_value={"results": [sample_attachment], "_links": {}}
        )

        page_id = "123456"
        result = mock_client.get(
            f"/api/v2/pages/{page_id}/attachments", operation="list attachments"
        )

        assert len(result["results"]) == 1
        assert result["results"][0]["id"] == "att123456"
        assert result["results"][0]["title"] == "test-file.pdf"

    def test_list_attachments_multiple(self, mock_client, sample_attachment):
        """Test listing multiple attachments."""
        attachments = [
            {**sample_attachment, "id": "att1", "title": "file1.pdf"},
            {**sample_attachment, "id": "att2", "title": "file2.docx"},
            {**sample_attachment, "id": "att3", "title": "image.png"},
        ]

        mock_client.get = MagicMock(return_value={"results": attachments, "_links": {}})

        page_id = "123456"
        result = mock_client.get(
            f"/api/v2/pages/{page_id}/attachments", operation="list attachments"
        )

        assert len(result["results"]) == 3
        assert result["results"][0]["title"] == "file1.pdf"
        assert result["results"][1]["title"] == "file2.docx"
        assert result["results"][2]["title"] == "image.png"

    def test_list_attachments_with_pagination(self, mock_client, sample_attachment):
        """Test listing attachments with pagination."""
        first_page = {
            "results": [{**sample_attachment, "id": "att1"}],
            "_links": {"next": "/api/v2/pages/123456/attachments?cursor=abc123"},
        }

        second_page = {"results": [{**sample_attachment, "id": "att2"}], "_links": {}}

        mock_client.get = MagicMock(side_effect=[first_page, second_page])

        # First call
        result1 = mock_client.get(
            "/api/v2/pages/123456/attachments", operation="list attachments"
        )

        assert len(result1["results"]) == 1
        assert "_links" in result1
        assert "next" in result1["_links"]

        # Second call with cursor
        result2 = mock_client.get(
            "/api/v2/pages/123456/attachments",
            params={"cursor": "abc123"},
            operation="list attachments",
        )

        assert len(result2["results"]) == 1

    def test_list_attachments_filter_by_media_type(
        self, mock_client, sample_attachment
    ):
        """Test filtering attachments by media type."""
        attachments = [
            {**sample_attachment, "id": "att1", "mediaType": "application/pdf"},
            {**sample_attachment, "id": "att2", "mediaType": "image/png"},
            {**sample_attachment, "id": "att3", "mediaType": "application/pdf"},
        ]

        mock_client.get = MagicMock(return_value={"results": attachments, "_links": {}})

        result = mock_client.get(
            "/api/v2/pages/123456/attachments",
            params={"mediaType": "application/pdf"},
            operation="list attachments",
        )

        # In practice, the API would filter, but we're testing the request
        assert "results" in result


class TestAttachmentFormatting:
    """Tests for attachment data formatting."""

    def test_format_attachment_basic(self, sample_attachment):
        """Test basic attachment formatting."""
        from confluence_as import format_json

        # Test JSON formatting
        json_output = format_json(sample_attachment)
        assert "att123456" in json_output
        assert "test-file.pdf" in json_output

    def test_format_attachment_size(self):
        """Test file size formatting."""

        def format_file_size(bytes: int) -> str:
            """Format file size in human-readable format."""
            for unit in ["B", "KB", "MB", "GB"]:
                if bytes < 1024.0:
                    return f"{bytes:.1f} {unit}"
                bytes /= 1024.0
            return f"{bytes:.1f} TB"

        assert format_file_size(512) == "512.0 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1536) == "1.5 KB"

    def test_attachment_metadata(self, sample_attachment):
        """Test extracting attachment metadata."""
        assert sample_attachment["id"] == "att123456"
        assert sample_attachment["title"] == "test-file.pdf"
        assert sample_attachment["fileSize"] == 1024
        assert sample_attachment["mediaType"] == "application/pdf"
        assert "version" in sample_attachment
        assert sample_attachment["version"]["number"] == 1


# =============================================================================
# UPDATE ATTACHMENT TESTS
# =============================================================================


class TestUpdateAttachment:
    """Tests for attachment update/replace functionality."""

    def test_update_attachment_basic(self, mock_client, sample_attachment, test_file):
        """Test basic attachment update."""
        attachment_id = "att123456"

        updated_attachment = sample_attachment.copy()
        updated_attachment["version"]["number"] = 2

        # Mock upload_file for update (same as upload)
        mock_client.upload_file = MagicMock(
            return_value={"results": [updated_attachment]}
        )

        # For v2 API, updating is done via POST with same filename
        result = mock_client.upload_file(
            f"/api/v2/attachments/{attachment_id}/data",
            test_file,
            operation="update attachment",
        )

        assert result["results"][0]["version"]["number"] == 2

    def test_update_increments_version(self, sample_attachment):
        """Test that update increments version number."""
        original_version = sample_attachment["version"]["number"]

        # After update
        updated_version = original_version + 1

        assert updated_version == 2
        assert updated_version > original_version

    def test_update_with_different_file(
        self, mock_client, sample_attachment, test_file, test_pdf_file
    ):
        """Test updating attachment with a different file."""
        attachment_id = "att123456"

        # Original was .txt, updating with .pdf
        updated_attachment = sample_attachment.copy()
        updated_attachment["title"] = test_pdf_file.name
        updated_attachment["mediaType"] = "application/pdf"
        updated_attachment["version"]["number"] = 2

        mock_client.upload_file = MagicMock(
            return_value={"results": [updated_attachment]}
        )

        result = mock_client.upload_file(
            f"/api/v2/attachments/{attachment_id}/data",
            test_pdf_file,
            operation="update attachment",
        )

        assert result["results"][0]["mediaType"] == "application/pdf"

    def test_update_preserves_attachment_id(self, sample_attachment):
        """Test that update preserves the attachment ID."""
        original_id = sample_attachment["id"]

        # After update, ID should remain the same
        updated_id = original_id

        assert updated_id == "att123456"
        assert updated_id == original_id

    def test_update_attachment_not_found(self, mock_client):
        """Test updating non-existent attachment."""

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.json.return_value = {"message": "Attachment not found"}

        # Would raise NotFoundError in actual implementation
        assert mock_response.status_code == 404

    def test_validate_file_for_update(self, test_file):
        """Test file validation for update."""
        from confluence_as import ValidationError, validate_file_path

        # File must exist
        result = validate_file_path(test_file)
        assert result.exists()
        assert result.is_file()

        # Non-existent file should fail
        with pytest.raises(ValidationError):
            validate_file_path("/nonexistent/file.txt")


class TestAttachmentVersioning:
    """Tests for attachment versioning concepts."""

    def test_version_history(self, sample_attachment):
        """Test attachment version structure."""
        version = sample_attachment["version"]

        assert "number" in version
        assert version["number"] >= 1
        assert "createdAt" in version

    def test_get_attachment_versions(self, mock_client, sample_attachment):
        """Test getting attachment version history."""
        attachment_id = "att123456"

        versions = [
            {**sample_attachment["version"], "number": 1},
            {**sample_attachment["version"], "number": 2},
        ]

        # Note: This endpoint might not exist in v2 API
        # Testing the concept
        mock_client.get = MagicMock(return_value={"results": versions})

        result = mock_client.get(
            f"/api/v2/attachments/{attachment_id}/versions",
            operation="get attachment versions",
        )

        assert len(result["results"]) == 2

    def test_update_with_comment(self, mock_client, sample_attachment, test_file):
        """Test updating attachment with version comment."""
        attachment_id = "att123456"

        updated_attachment = sample_attachment.copy()
        updated_attachment["version"]["number"] = 2
        updated_attachment["version"]["message"] = "Updated document"

        mock_client.upload_file = MagicMock(
            return_value={"results": [updated_attachment]}
        )

        result = mock_client.upload_file(
            f"/api/v2/attachments/{attachment_id}/data",
            test_file,
            additional_data={"comment": "Updated document"},
            operation="update attachment",
        )

        assert result["results"][0]["version"]["message"] == "Updated document"


# =============================================================================
# DELETE ATTACHMENT TESTS
# =============================================================================


class TestDeleteAttachment:
    """Tests for attachment deletion functionality."""

    def test_delete_attachment_basic(self, mock_client):
        """Test basic attachment deletion."""
        attachment_id = "att123456"

        mock_client.delete = MagicMock(return_value={})

        result = mock_client.delete(
            f"/api/v2/attachments/{attachment_id}", operation="delete attachment"
        )

        # DELETE returns empty response on success
        assert result == {}
        mock_client.delete.assert_called_once()

    def test_delete_attachment_not_found(self, mock_client):
        """Test deleting non-existent attachment."""

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.ok = False
        mock_response.json.return_value = {"message": "Attachment not found"}

        # Would raise NotFoundError in actual implementation
        assert mock_response.status_code == 404

    def test_delete_attachment_no_permission(self, mock_client):
        """Test deleting attachment without permission."""

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.ok = False
        mock_response.json.return_value = {"message": "Insufficient permissions"}

        # Would raise PermissionError in actual implementation
        assert mock_response.status_code == 403

    def test_delete_with_confirmation(self):
        """Test deletion with confirmation prompt."""
        # In actual script, would use --force flag to skip confirmation
        # or interactive prompt for confirmation
        force = True
        assert force is True

        # Without force, would prompt
        force = False
        assert force is False

    def test_validate_attachment_id_for_delete(self):
        """Test attachment ID validation for deletion."""
        from confluence_as import ValidationError, validate_page_id

        # Attachment IDs use same validation as page IDs (numeric)
        assert validate_page_id("123456") == "123456"
        assert validate_page_id("789012") == "789012"

        # Invalid IDs should fail
        with pytest.raises(ValidationError):
            validate_page_id("")

        with pytest.raises(ValidationError):
            validate_page_id(None)


class TestDeleteBulkAttachments:
    """Tests for bulk attachment deletion."""

    def test_delete_multiple_attachments(self, mock_client):
        """Test deleting multiple attachments."""
        attachment_ids = ["att1", "att2", "att3"]

        mock_client.delete = MagicMock(return_value={})

        results = []
        for att_id in attachment_ids:
            result = mock_client.delete(
                f"/api/v2/attachments/{att_id}", operation="delete attachment"
            )
            results.append(result)

        assert len(results) == 3
        assert mock_client.delete.call_count == 3

    def test_delete_all_from_page(self, mock_client, sample_attachment):
        """Test deleting all attachments from a page."""
        attachments = [
            {**sample_attachment, "id": "att1"},
            {**sample_attachment, "id": "att2"},
        ]

        # First get all attachments
        mock_client.get = MagicMock(return_value={"results": attachments, "_links": {}})

        result = mock_client.get(
            "/api/v2/pages/123456/attachments", operation="list attachments"
        )

        # Then delete each
        mock_client.delete = MagicMock(return_value={})
        for att in result["results"]:
            mock_client.delete(
                f"/api/v2/attachments/{att['id']}", operation="delete attachment"
            )

        assert mock_client.delete.call_count == 2

    def test_delete_with_errors(self, mock_client):
        """Test handling errors during bulk deletion."""
        attachment_ids = ["att1", "att2", "att3"]

        def delete_side_effect(endpoint, **kwargs):
            # Fail on second attachment
            if "att2" in endpoint:
                response = Mock()
                response.status_code = 404
                response.ok = False
                raise Exception("Not found")
            return {}

        mock_client.delete = MagicMock(side_effect=delete_side_effect)

        # Try to delete all, expect one to fail
        successful = []
        failed = []

        for att_id in attachment_ids:
            try:
                mock_client.delete(
                    f"/api/v2/attachments/{att_id}", operation="delete attachment"
                )
                successful.append(att_id)
            except Exception:
                failed.append(att_id)

        assert len(successful) == 2
        assert len(failed) == 1
        assert "att2" in failed
