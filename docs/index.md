# Confluence Assistant Skills Library

Python library for Confluence Cloud REST API - shared utilities for Confluence automation.

## Overview

This library provides a complete toolkit for building Confluence integrations:

- **[Client](api/client.md)** - HTTP client with retry logic, pagination, and file operations
- **[Validators](api/validators.md)** - Input validation for page IDs, space keys, CQL, etc.
- **[Formatters](api/formatters.md)** - Output formatting for pages, tables, JSON, CSV
- **[ADF Helper](api/adf.md)** - Atlassian Document Format conversion
- **[XHTML Helper](api/xhtml.md)** - Legacy storage format conversion
- **[Error Handling](api/errors.md)** - Exception hierarchy for API errors

## Installation

```bash
pip install confluence-as
```

## Quick Start

```python
from confluence_as import (
    get_confluence_client,
    validate_page_id,
    format_page,
    markdown_to_adf,
)

# Set environment variables:
# CONFLUENCE_SITE_URL=https://your-site.atlassian.net
# CONFLUENCE_EMAIL=your-email@example.com
# CONFLUENCE_API_TOKEN=your-api-token

# Get a configured client
client = get_confluence_client()

# Get a page
page_id = validate_page_id("12345")
page = client.get(f"/api/v2/pages/{page_id}")
print(format_page(page))

# Create content from Markdown
content = markdown_to_adf("# Hello\n\nThis is **bold** text.")
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `CONFLUENCE_SITE_URL` | Yes | Confluence Cloud URL (e.g., `https://your-site.atlassian.net`) |
| `CONFLUENCE_EMAIL` | Yes | Email for API authentication |
| `CONFLUENCE_API_TOKEN` | Yes | API token from [Atlassian Account](https://id.atlassian.com/manage-profile/security/api-tokens) |

### Programmatic Configuration

```python
from confluence_as import ConfluenceClient

client = ConfluenceClient(
    base_url="https://your-site.atlassian.net",
    email="your-email@example.com",
    api_token="your-api-token",
    timeout=30,          # Request timeout in seconds
    max_retries=3,       # Retry attempts for 429/5xx errors
    retry_backoff=2.0,   # Exponential backoff multiplier
    verify_ssl=True,     # SSL certificate verification
)
```

## Examples

See the [Examples](examples.md) page for detailed usage examples covering:

- Page CRUD operations
- Search and CQL queries
- Bulk operations
- Content conversion
- File attachments

## API Reference

- [Client API](api/client.md)
- [Validators](api/validators.md)
- [Formatters](api/formatters.md)
- [ADF Helper](api/adf.md)
- [XHTML Helper](api/xhtml.md)
- [Error Handling](api/errors.md)
