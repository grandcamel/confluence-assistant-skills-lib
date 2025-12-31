# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Python library providing shared utilities for Confluence Cloud REST API automation. This is a dependency of the [Confluence Assistant Skills](https://github.com/grandcamel/Confluence-Assistant-Skills) project.

## Development Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/confluence_assistant_skills_lib

# Run a single test file
pytest tests/test_validators.py

# Run a specific test
pytest tests/test_validators.py::test_validate_page_id
```

## Architecture

The library is organized into focused modules under `src/confluence_assistant_skills_lib/`:

- **confluence_client.py** - HTTP client with retry logic, pagination, and file upload/download. Uses `requests` with exponential backoff for 429/5xx errors.
- **config_manager.py** - Multi-source configuration from environment variables and JSON profiles (`.claude/settings.local.json`)
- **error_handler.py** - Exception hierarchy mapping HTTP status codes to specific error types (`AuthenticationError`, `NotFoundError`, `RateLimitError`, etc.)
- **validators.py** - Input validation functions that raise `ValidationError` on failure
- **formatters.py** - Output formatting for pages, spaces, tables, JSON, and CSV export
- **adf_helper.py** - Atlassian Document Format (ADF) conversion: Markdown ↔ ADF, programmatic node creation
- **xhtml_helper.py** - Legacy XHTML storage format conversion

## Key Patterns

- All public APIs are re-exported from `__init__.py` for convenient imports
- Cache functionality is inherited from `assistant-skills-lib` base library
- Confluence API endpoints use `/wiki` prefix in URLs; the client handles this automatically
- Supports both v2 (`/api/v2`) and legacy v1 (`/rest/api`) Confluence endpoints

## Required Environment Variables

```bash
CONFLUENCE_SITE_URL=https://your-site.atlassian.net
CONFLUENCE_EMAIL=your-email@example.com
CONFLUENCE_API_TOKEN=your-api-token
```
