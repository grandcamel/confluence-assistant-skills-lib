# XHTML Helper

Utilities for working with Confluence's legacy XHTML storage format.

## Overview

XHTML storage format is used by:
- Confluence v1 API (`/rest/api/content`)
- Legacy content predating v2 API
- Some Confluence macros and plugins

This module provides:
- Convert XHTML to Markdown
- Convert Markdown to XHTML
- Convert between XHTML and ADF (for v1/v2 migration)
- Handle Confluence-specific macros

See [Confluence Storage Format Documentation](https://confluence.atlassian.com/doc/confluence-storage-format-790796544.html).

## Conversion Functions

### xhtml_to_markdown()

```python
def xhtml_to_markdown(xhtml: str) -> str
```

Convert Confluence XHTML storage format to Markdown.

**Handles:**
- Paragraphs, headings, lists
- Bold, italic, underline, strikethrough
- Links and images
- Code blocks and inline code
- Tables
- Common Confluence macros (code, info, warning, note, expand)

**Example:**
```python
from confluence_assistant_skills import xhtml_to_markdown

# From v1 API response
page = client.get("/rest/api/content/12345?expand=body.storage")
xhtml = page["body"]["storage"]["value"]
markdown = xhtml_to_markdown(xhtml)
print(markdown)
```

### markdown_to_xhtml()

```python
def markdown_to_xhtml(markdown: str) -> str
```

Convert Markdown to Confluence XHTML storage format.

**Example:**
```python
from confluence_assistant_skills import markdown_to_xhtml

markdown = """
# Welcome

This is **bold** text.

- Item one
- Item two
"""

xhtml = markdown_to_xhtml(markdown)
# <h1>Welcome</h1><p>This is <strong>bold</strong> text.</p><ul><li>Item one</li><li>Item two</li></ul>

# Use with v1 API
client.put("/rest/api/content/12345", json_data={
    "type": "page",
    "title": "My Page",
    "body": {
        "storage": {
            "value": xhtml,
            "representation": "storage"
        }
    },
    "version": {"number": 2}
})
```

## V1/V2 Format Migration

### xhtml_to_adf()

```python
def xhtml_to_adf(xhtml: str) -> dict
```

Convert XHTML storage format to ADF.

Useful for migrating content from v1 API format to v2 API format.

**Example:**
```python
from confluence_assistant_skills import xhtml_to_adf

# Get page from v1 API
v1_page = client.get("/rest/api/content/12345?expand=body.storage")
xhtml = v1_page["body"]["storage"]["value"]

# Convert to ADF
adf = xhtml_to_adf(xhtml)

# Use with v2 API
client.put("/api/v2/pages/12345", json_data={
    "id": "12345",
    "title": "Migrated Page",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(adf)
    },
    "version": {"number": 2}
})
```

### adf_to_xhtml()

```python
def adf_to_xhtml(adf: dict) -> str
```

Convert ADF to XHTML storage format.

Useful for using v2 content with v1 API endpoints.

**Example:**
```python
from confluence_assistant_skills import adf_to_xhtml

# Get page from v2 API
v2_page = client.get("/api/v2/pages/12345?body-format=atlas_doc_format")
adf = json.loads(v2_page["body"]["atlas_doc_format"]["value"])

# Convert to XHTML for v1 API compatibility
xhtml = adf_to_xhtml(adf)
```

## Utility Functions

### extract_text_from_xhtml()

```python
def extract_text_from_xhtml(xhtml: str) -> str
```

Extract plain text from XHTML content, removing all tags.

**Example:**
```python
from confluence_assistant_skills import extract_text_from_xhtml

xhtml = "<p>Hello <strong>World</strong></p>"
text = extract_text_from_xhtml(xhtml)
# "Hello World"
```

### wrap_in_storage_format()

```python
def wrap_in_storage_format(content: str) -> str
```

Wrap content in proper Confluence storage format structure.

### validate_xhtml()

```python
def validate_xhtml(xhtml: str) -> tuple[bool, str | None]
```

Validate XHTML storage format.

**Example:**
```python
from confluence_assistant_skills import validate_xhtml

is_valid, error = validate_xhtml(xhtml)
if not is_valid:
    print(f"Invalid XHTML: {error}")
```

**Checks:**
- Balanced opening/closing tags
- Properly nested elements

## Macro Handling

The `xhtml_to_markdown()` function handles common Confluence macros:

| Macro | Markdown Output |
|-------|----------------|
| `code` | Fenced code block with language |
| `info` | Blockquote with "Info:" prefix |
| `warning` | Blockquote with "Warning:" prefix |
| `note` | Blockquote with "Note:" prefix |
| `tip` | Blockquote with "Tip:" prefix |
| `panel` | Blockquote with "Panel:" prefix |
| `status` | Inline code |
| `toc` | `[Table of Contents]` placeholder |
| `expand` | HTML `<details>` element |
