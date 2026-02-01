"""
Unit tests for template operations.

Consolidated from Confluence-Assistant-Skills:
- skills/confluence-template/tests/test_create_template.py
- skills/confluence-template/tests/test_get_template.py
- skills/confluence-template/tests/test_list_templates.py
- skills/confluence-template/tests/test_update_template.py
- skills/confluence-template/tests/test_create_from_template.py
"""


# =============================================================================
# CREATE TEMPLATE TESTS
# =============================================================================


class TestCreateTemplate:
    """Tests for creating new templates."""

    def test_create_template_minimal(self, mock_client, sample_template):
        """Test creating a template with minimal fields."""
        mock_client.setup_response("post", sample_template)

        # Would execute: python create_template.py --name "My Template" --space DOCS
        # Verify POST to /rest/api/template

    def test_create_template_with_description(self, mock_client, sample_template):
        """Test creating a template with description."""
        mock_client.setup_response("post", sample_template)

        # Would execute with --description "Template description"
        # Verify description is included

    def test_create_template_with_body_from_file(
        self, mock_client, sample_template, tmp_path
    ):
        """Test creating template with body from file."""
        # Create test file
        template_file = tmp_path / "template.html"
        template_file.write_text("<h1>Template</h1>")

        mock_client.setup_response("post", sample_template)

        # Would execute with --file template.html
        # Verify file content is read and used

    def test_create_template_with_markdown(
        self, mock_client, sample_template, tmp_path
    ):
        """Test creating template from Markdown."""
        md_file = tmp_path / "template.md"
        md_file.write_text("# Template\n\nContent here")

        mock_client.setup_response("post", sample_template)

        # Would execute with --file template.md
        # Verify Markdown is converted to storage format

    def test_create_template_with_labels(self, mock_client, sample_template):
        """Test creating template with labels."""
        mock_client.setup_response("post", sample_template)

        # Would execute with --labels "template,meeting"
        # Verify labels are included

    def test_create_template_invalid_space(self, mock_client):
        """Test creating template in non-existent space."""

        # Invalid space should fail validation

    def test_create_template_duplicate_name(self, mock_client):
        """Test creating template with duplicate name."""

        mock_client.setup_response(
            "post", {"message": "Template already exists"}, status_code=409
        )

        # Should raise ConflictError

    def test_validate_template_name(self):
        """Test template name validation."""

        # Empty name should fail
        # Very long name should fail
        # Valid name should pass


class TestCreateBlueprintTemplate:
    """Tests for creating blueprint-based templates."""

    def test_create_from_blueprint_id(self, mock_client, sample_template):
        """Test creating template based on blueprint."""
        mock_client.setup_response("post", sample_template)

        # Would execute with --blueprint-id com.atlassian...
        # Verify contentBlueprintId is set

    def test_create_blueprint_with_module_key(self, mock_client, sample_template):
        """Test creating with module complete key."""
        mock_client.setup_response("post", sample_template)

        # Verify moduleCompleteKey parameter


# =============================================================================
# GET TEMPLATE TESTS
# =============================================================================


class TestGetTemplate:
    """Tests for getting template details."""

    def test_get_template_success(self, mock_client, sample_template):
        """Test successfully retrieving a template."""
        mock_client.setup_response("get", sample_template)

        # Would execute: python get_template.py tmpl-123
        # Verify calls GET /rest/api/template/tmpl-123

    def test_get_template_with_body(self, mock_client, sample_template):
        """Test retrieving template with body content."""
        mock_client.setup_response("get", sample_template)

        # Would execute with --body flag
        # Verify body content is included in output

    def test_get_template_json_output(self, mock_client, sample_template):
        """Test JSON output format."""
        mock_client.setup_response("get", sample_template)

        # Would execute with --output json
        # Verify JSON is properly formatted

    def test_get_template_not_found(self, mock_client):
        """Test handling of non-existent template."""

        mock_client.setup_response(
            "get", {"message": "Template not found"}, status_code=404
        )

        # Should raise NotFoundError
        # Should provide helpful error message

    def test_get_template_markdown_format(self, mock_client, sample_template):
        """Test converting template body to Markdown."""
        mock_client.setup_response("get", sample_template)

        # Would execute with --format markdown
        # Verify XHTML is converted to Markdown

    def test_validate_template_id(self):
        """Test template ID validation."""

        # Template IDs can be various formats
        # Should validate non-empty string


class TestGetBlueprint:
    """Tests for getting blueprint details."""

    def test_get_blueprint_success(self, mock_client, sample_blueprint):
        """Test successfully retrieving a blueprint."""
        mock_client.setup_response("get", sample_blueprint)

        # Would execute with --blueprint flag
        # Verify calls correct API endpoint

    def test_get_blueprint_metadata(self, mock_client, sample_blueprint):
        """Test retrieving blueprint metadata."""
        mock_client.setup_response("get", sample_blueprint)

        # Verify module keys and IDs are displayed


# =============================================================================
# LIST TEMPLATES TESTS
# =============================================================================


class TestListTemplates:
    """Tests for listing templates functionality."""

    def test_list_templates_default(self, mock_client, sample_template):
        """Test listing all templates without filters."""
        # Setup mock response
        mock_client.setup_response(
            "get", {"results": [sample_template], "size": 1, "start": 0, "limit": 25}
        )

        # Would execute list_templates.py
        # Verify it calls GET /rest/api/template/page
        # Verify output contains template name

    def test_list_templates_by_space(self, mock_client, sample_template):
        """Test listing templates filtered by space."""
        mock_client.setup_response("get", {"results": [sample_template], "size": 1})

        # Would execute with --space DOCS
        # Verify spaceKey parameter is passed

    def test_list_templates_by_type_page(self, mock_client, sample_template):
        """Test listing page templates only."""
        mock_client.setup_response("get", {"results": [sample_template]})

        # Would execute with --type page
        # Verify filtering works

    def test_list_templates_by_type_blogpost(self, mock_client):
        """Test listing blogpost templates."""
        mock_client.setup_response("get", {"results": []})

        # Would execute with --type blogpost
        # Verify correct API endpoint is used

    def test_list_templates_empty_results(self, mock_client):
        """Test handling of empty template list."""
        mock_client.setup_response("get", {"results": [], "size": 0})

        # Should not error on empty results
        # Should display appropriate message

    def test_list_templates_json_output(self, mock_client, sample_template):
        """Test JSON output format."""
        mock_client.setup_response("get", {"results": [sample_template]})

        # Would execute with --output json
        # Verify JSON formatting

    def test_list_blueprints(self, mock_client, sample_blueprint):
        """Test listing blueprints."""
        mock_client.setup_response("get", {"results": [sample_blueprint]})

        # Would execute with --blueprints flag
        # Verify calls /rest/api/template/blueprint

    def test_list_templates_pagination(self, mock_client, sample_template):
        """Test pagination handling."""
        # First page

        # Second page

        # Would verify pagination is handled correctly

    def test_validate_template_type_invalid(self):
        """Test that invalid template types fail validation."""

        # Custom validator for template type
        # Should only accept 'page' or 'blogpost'


class TestTemplateValidators:
    """Tests for template-specific validators."""

    def test_validate_template_id_valid(self):
        """Test valid template ID validation."""
        # Would need a validate_template_id function
        # Similar to validate_page_id

    def test_validate_template_id_invalid(self):
        """Test invalid template ID validation."""

        # Empty template ID should fail
        # None should fail


# =============================================================================
# UPDATE TEMPLATE TESTS
# =============================================================================


class TestUpdateTemplate:
    """Tests for updating existing templates."""

    def test_update_template_name(self, mock_client, sample_template):
        """Test updating template name."""
        # Mock getting current template
        mock_client.setup_response("get", sample_template)

        # Mock update
        updated = sample_template.copy()
        updated["name"] = "Updated Template"
        mock_client.setup_response("put", updated)

        # Would execute: python update_template.py tmpl-123 --name "Updated Template"
        # Verify PUT to /rest/api/template/tmpl-123

    def test_update_template_description(self, mock_client, sample_template):
        """Test updating template description."""
        mock_client.setup_response("get", sample_template)
        updated = sample_template.copy()
        updated["description"] = "New description"
        mock_client.setup_response("put", updated)

        # Would execute with --description "New description"

    def test_update_template_body(self, mock_client, sample_template):
        """Test updating template body content."""
        mock_client.setup_response("get", sample_template)

        updated = sample_template.copy()
        updated["body"]["storage"]["value"] = "<h1>Updated</h1>"
        mock_client.setup_response("put", updated)

        # Would execute with --content or --file

    def test_update_template_body_from_file(
        self, mock_client, sample_template, tmp_path
    ):
        """Test updating template body from file."""
        template_file = tmp_path / "updated.html"
        template_file.write_text("<h1>Updated Content</h1>")

        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("put", sample_template)

        # Would execute with --file updated.html

    def test_update_template_markdown(self, mock_client, sample_template, tmp_path):
        """Test updating with Markdown file."""
        md_file = tmp_path / "updated.md"
        md_file.write_text("# Updated\n\nNew content")

        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("put", sample_template)

        # Would execute with --file updated.md
        # Verify Markdown conversion

    def test_update_template_add_labels(self, mock_client, sample_template):
        """Test adding labels to template."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("put", sample_template)

        # Would execute with --add-labels "new-label"

    def test_update_template_remove_labels(self, mock_client, sample_template):
        """Test removing labels from template."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("put", sample_template)

        # Would execute with --remove-labels "old-label"

    def test_update_template_not_found(self, mock_client):
        """Test updating non-existent template."""

        mock_client.setup_response(
            "get", {"message": "Template not found"}, status_code=404
        )

        # Should raise NotFoundError

    def test_update_template_no_changes(self, mock_client, sample_template):
        """Test update with no changes provided."""

        # Should require at least one field to update

    def test_update_preserves_existing_fields(self, mock_client, sample_template):
        """Test that update preserves fields not being changed."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("put", sample_template)

        # When updating name only, description and body should remain
        # Verify GET is called first to retrieve current state


class TestTemplateVersioning:
    """Tests for template version management."""

    def test_update_increments_version(self, mock_client, sample_template):
        """Test that updating increments version number."""
        # Templates may have version tracking
        # Verify version handling

    def test_update_with_version_conflict(self, mock_client):
        """Test handling version conflicts."""

        # If template was modified by another user
        # Should detect and handle conflict


# =============================================================================
# CREATE FROM TEMPLATE TESTS
# =============================================================================


class TestCreateFromTemplate:
    """Tests for creating pages from templates."""

    def test_create_page_from_template_minimal(
        self, mock_client, sample_template, sample_page
    ):
        """Test creating a page with minimal arguments."""
        # Mock template lookup
        mock_client.setup_response("get", sample_template)
        # Mock page creation
        mock_client.setup_response("post", sample_page)

        # Would execute: python create_from_template.py --template tmpl-123 --space DOCS --title "New Page"
        # Verify POST to /rest/api/content with templateId

    def test_create_page_from_template_with_parent(
        self, mock_client, sample_template, sample_page
    ):
        """Test creating a page under a parent."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("post", sample_page)

        # Would execute with --parent-id 12345
        # Verify ancestors array is set

    def test_create_page_from_template_with_labels(
        self, mock_client, sample_template, sample_page
    ):
        """Test creating a page with labels."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("post", sample_page)

        # Would execute with --labels "label1,label2"
        # Verify labels are added to request

    def test_create_from_template_not_found(self, mock_client):
        """Test creating from non-existent template."""

        mock_client.setup_response(
            "get", {"message": "Template not found"}, status_code=404
        )

        # Should raise NotFoundError

    def test_create_from_template_invalid_space(self, mock_client, sample_template):
        """Test creating in non-existent space."""

        mock_client.setup_response("get", sample_template)

        # Invalid space key should fail validation

    def test_create_from_blueprint(self, mock_client, sample_blueprint, sample_page):
        """Test creating from a blueprint."""
        mock_client.setup_response("get", sample_blueprint)
        mock_client.setup_response("post", sample_page)

        # Would execute with --blueprint flag
        # Verify correct API parameters for blueprint

    def test_create_from_template_with_content_override(
        self, mock_client, sample_template, sample_page
    ):
        """Test creating from template but overriding content."""
        mock_client.setup_response("get", sample_template)
        mock_client.setup_response("post", sample_page)

        # Would execute with --content or --file
        # Verify template is used as base but content is replaced

    def test_validate_required_fields(self):
        """Test that required fields are validated."""

        # Should require: template ID, space, title


class TestTemplateContentMerging:
    """Tests for merging template content with user input."""

    def test_merge_template_with_custom_content(self):
        """Test merging template structure with custom content."""
        # Template might have placeholders
        # User content should replace or merge appropriately

    def test_preserve_template_structure(self):
        """Test that template structure is preserved."""
        # Custom content should maintain template layout
