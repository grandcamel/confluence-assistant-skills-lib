"""Integration tests for confluence-assistant-skills library.

These tests verify that the library components work together correctly
without requiring external services (Confluence API).
"""

import os
from unittest.mock import patch

import pytest
import responses

from confluence_assistant_skills import (
    ConfigManager,
    ConfluenceClient,
    adf_to_markdown,
    adf_to_text,
    create_adf_doc,
    create_bullet_list,
    create_heading,
    create_paragraph,
    export_csv,
    format_page,
    format_search_results,
    format_space,
    format_table,
    get_confluence_client,
    markdown_to_adf,
    markdown_to_xhtml,
    text_to_adf,
    validate_cql,
    validate_page_id,
    validate_space_key,
    xhtml_to_markdown,
)

pytestmark = pytest.mark.integration


class TestContentConversionPipeline:
    """Test content conversion workflows."""

    def test_markdown_to_adf_to_markdown_roundtrip(self):
        """Markdown can be converted to ADF and back."""
        original = """# My Document

This is a paragraph with **bold** and *italic* text.

- Item 1
- Item 2
- Item 3

```python
print("Hello, World!")
```
"""
        # Convert to ADF
        adf = markdown_to_adf(original)
        assert adf["type"] == "doc"
        assert len(adf["content"]) > 0

        # Convert back to Markdown
        result = adf_to_markdown(adf)

        # Key content should be preserved
        assert "My Document" in result
        assert "**bold**" in result
        assert "*italic*" in result
        assert "- Item 1" in result
        assert "print" in result

    def test_text_to_adf_to_text_roundtrip(self):
        """Plain text can be converted to ADF and back."""
        original = "First paragraph.\n\nSecond paragraph."

        adf = text_to_adf(original)
        result = adf_to_text(adf)

        assert "First paragraph" in result
        assert "Second paragraph" in result

    def test_markdown_to_xhtml_to_markdown_roundtrip(self):
        """Markdown can be converted to XHTML and back."""
        original = "# Heading\n\nParagraph with **bold** text."

        xhtml = markdown_to_xhtml(original)
        assert "<h1>" in xhtml
        assert "<strong>" in xhtml

        result = xhtml_to_markdown(xhtml)
        assert "Heading" in result
        assert "bold" in result

    def test_build_complex_adf_document(self):
        """Build a complex ADF document programmatically."""
        doc = create_adf_doc(
            [
                create_heading("Welcome", level=1),
                create_paragraph(text="This is the introduction."),
                create_heading("Features", level=2),
                create_bullet_list(["Feature A", "Feature B", "Feature C"]),
            ]
        )

        # Verify structure
        assert doc["type"] == "doc"
        assert len(doc["content"]) == 4
        assert doc["content"][0]["type"] == "heading"
        assert doc["content"][1]["type"] == "paragraph"
        assert doc["content"][3]["type"] == "bulletList"

        # Convert to text
        text = adf_to_text(doc)
        assert "Welcome" in text
        assert "introduction" in text
        assert "Feature A" in text


class TestValidationWorkflow:
    """Test input validation across components."""

    def test_validate_and_format_page_id(self):
        """Validate page ID and use it in formatting."""
        # Valid page ID
        page_id = validate_page_id("12345")
        assert page_id == "12345"

        # Create mock page data
        page = {
            "id": page_id,
            "title": "Test Page",
            "status": "current",
            "spaceId": "123",
        }

        # Format should work
        result = format_page(page)
        assert "Test Page" in result
        assert "12345" in result

    def test_validate_and_format_space_key(self):
        """Validate space key and use it in formatting."""
        # Valid space key (gets normalized to uppercase)
        space_key = validate_space_key("docs")
        assert space_key == "DOCS"

        # Create mock space data
        space = {
            "key": space_key,
            "name": "Documentation",
            "type": "global",
            "status": "current",
        }

        # Format should work
        result = format_space(space)
        assert "Documentation" in result
        assert "DOCS" in result

    def test_validate_cql_and_format_results(self):
        """Validate CQL and format search results."""
        # Valid CQL - validate it doesn't raise
        validate_cql('space = "DOCS" AND type = page')

        # Create mock search results
        results = [
            {
                "content": {
                    "id": "123",
                    "title": "Page 1",
                    "type": "page",
                    "space": {"key": "DOCS"},
                }
            },
            {
                "content": {
                    "id": "456",
                    "title": "Page 2",
                    "type": "page",
                    "space": {"key": "DOCS"},
                }
            },
        ]

        # Format should work
        result = format_search_results(results)
        assert "Page 1" in result
        assert "Page 2" in result


class TestFormattingPipeline:
    """Test formatting workflows."""

    def test_format_table_from_api_data(self):
        """Format tabular data from API response."""
        # Simulate API response data
        pages = [
            {"id": "1", "title": "Home", "status": "current"},
            {"id": "2", "title": "Getting Started", "status": "current"},
            {"id": "3", "title": "API Reference", "status": "draft"},
        ]

        result = format_table(
            pages,
            columns=["id", "title", "status"],
            headers=["ID", "Title", "Status"],
        )

        assert "Home" in result
        assert "Getting Started" in result
        assert "draft" in result

    def test_export_csv_from_search_results(self, tmp_path):
        """Export search results to CSV."""
        results = [
            {"id": "1", "title": "Page A", "views": 100},
            {"id": "2", "title": "Page B", "views": 50},
        ]

        output_path = tmp_path / "results.csv"
        export_csv(results, output_path)

        content = output_path.read_text()
        assert "id,title,views" in content
        assert "Page A" in content
        assert "100" in content


class TestClientConfigurationFlow:
    """Test client configuration and creation."""

    def test_config_manager_with_environment(self):
        """ConfigManager loads from environment variables."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_SITE_URL": "https://test.atlassian.net",
                "CONFLUENCE_EMAIL": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            # Clear singleton
            ConfigManager._instances = {}

            manager = ConfigManager()
            credentials = manager.get_credentials()

            assert credentials["url"] == "https://test.atlassian.net"
            assert credentials["email"] == "test@example.com"
            assert credentials["api_token"] == "test-token"

    def test_get_confluence_client_integration(self):
        """get_confluence_client creates a properly configured client."""
        with patch.dict(
            os.environ,
            {
                "CONFLUENCE_SITE_URL": "https://test.atlassian.net",
                "CONFLUENCE_EMAIL": "test@example.com",
                "CONFLUENCE_API_TOKEN": "test-token",
            },
        ):
            # Clear singleton
            ConfigManager._instances = {}

            client = get_confluence_client()

            assert isinstance(client, ConfluenceClient)
            assert client.base_url == "https://test.atlassian.net"
            assert client.email == "test@example.com"


class TestAPIWorkflowMocked:
    """Test API workflows with mocked responses."""

    @responses.activate
    def test_fetch_and_format_page(self):
        """Fetch a page and format it for display."""
        # Mock the API response
        responses.add(
            responses.GET,
            "https://test.atlassian.net/wiki/api/v2/pages/12345",
            json={
                "id": "12345",
                "title": "My Page",
                "status": "current",
                "spaceId": "123",
                "body": {"storage": {"value": "<p>Hello <strong>World</strong></p>"}},
            },
            status=200,
        )

        # Create client and fetch
        client = ConfluenceClient(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test-token",
        )

        page = client.get("/api/v2/pages/12345")

        # Format the page
        formatted = format_page(page)
        assert "My Page" in formatted
        assert "12345" in formatted

        # Convert body to markdown
        body_xhtml = page["body"]["storage"]["value"]
        markdown = xhtml_to_markdown(body_xhtml)
        assert "World" in markdown

    @responses.activate
    def test_paginate_and_format_results(self):
        """Paginate through results and format them."""
        # Mock first page
        responses.add(
            responses.GET,
            "https://test.atlassian.net/wiki/api/v2/pages",
            json={
                "results": [
                    {"id": "1", "title": "Page 1", "status": "current"},
                    {"id": "2", "title": "Page 2", "status": "current"},
                ],
                "_links": {"next": "/api/v2/pages?cursor=abc"},
            },
            status=200,
        )

        # Mock second page
        responses.add(
            responses.GET,
            "https://test.atlassian.net/wiki/api/v2/pages",
            json={
                "results": [
                    {"id": "3", "title": "Page 3", "status": "current"},
                ],
                "_links": {},
            },
            status=200,
        )

        # Create client and paginate
        client = ConfluenceClient(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test-token",
        )

        all_pages = list(client.paginate("/api/v2/pages"))
        assert len(all_pages) == 3

        # Format as table
        table = format_table(
            all_pages,
            columns=["id", "title"],
            headers=["ID", "Title"],
        )
        assert "Page 1" in table
        assert "Page 2" in table
        assert "Page 3" in table

    @responses.activate
    def test_search_and_export_workflow(self, tmp_path):
        """Search for pages and export results."""
        # Mock search response
        responses.add(
            responses.GET,
            "https://test.atlassian.net/wiki/rest/api/content/search",
            json={
                "results": [
                    {
                        "content": {
                            "id": "1",
                            "title": "Result 1",
                            "type": "page",
                        },
                        "excerpt": "Found match here",
                    },
                    {
                        "content": {
                            "id": "2",
                            "title": "Result 2",
                            "type": "page",
                        },
                        "excerpt": "Another match",
                    },
                ],
                "_links": {},
            },
            status=200,
        )

        client = ConfluenceClient(
            base_url="https://test.atlassian.net",
            email="test@example.com",
            api_token="test-token",
        )

        # Search
        result = client.get(
            "/rest/api/content/search",
            params={"cql": 'space = "DOCS"'},
        )

        # Format for display
        formatted = format_search_results(result["results"], show_excerpt=True)
        assert "Result 1" in formatted
        assert "match" in formatted.lower()

        # Export to CSV
        export_data = [
            {"id": r["content"]["id"], "title": r["content"]["title"]}
            for r in result["results"]
        ]
        csv_path = tmp_path / "search_results.csv"
        export_csv(export_data, csv_path)

        content = csv_path.read_text()
        assert "Result 1" in content
        assert "Result 2" in content
