# ADF Helper

Atlassian Document Format (ADF) utilities for working with Confluence Cloud API v2.

## Overview

ADF is the JSON-based document format used by Confluence Cloud's v2 API. This module provides:

- Convert plain text to ADF
- Convert Markdown to ADF
- Convert ADF to plain text
- Convert ADF to Markdown
- Programmatic ADF node creation

See [Atlassian ADF Documentation](https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/) for format details.

## Conversion Functions

### markdown_to_adf()

```python
def markdown_to_adf(markdown: str) -> dict
```

Convert Markdown to ADF.

**Supported Markdown:**
- Headings (`# to ######`)
- Bold (`**text**` or `__text__`)
- Italic (`*text*` or `_text_`)
- Code (inline `` `code` `` and fenced blocks)
- Links `[text](url)`
- Bullet lists (`-` or `*`)
- Ordered lists (`1.`, `2.`, etc.)
- Blockquotes (`>`)
- Horizontal rules (`---`)

**Example:**
```python
from confluence_assistant_skills import markdown_to_adf

adf = markdown_to_adf("""
# Welcome

This is **bold** and *italic* text.

- Item one
- Item two
""")

# Use with API v2
client.post("/api/v2/pages", json_data={
    "spaceId": "123456",
    "title": "My Page",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(adf)
    }
})
```

### text_to_adf()

```python
def text_to_adf(text: str) -> dict
```

Convert plain text to ADF.

**Example:**
```python
from confluence_assistant_skills import text_to_adf

adf = text_to_adf("Hello, world!\n\nThis is a new paragraph.")
```

### adf_to_markdown()

```python
def adf_to_markdown(adf: dict) -> str
```

Convert ADF to Markdown.

**Example:**
```python
from confluence_assistant_skills import adf_to_markdown

page = client.get("/api/v2/pages/12345?body-format=atlas_doc_format")
adf = json.loads(page["body"]["atlas_doc_format"]["value"])
markdown = adf_to_markdown(adf)
print(markdown)
```

### adf_to_text()

```python
def adf_to_text(adf: dict) -> str
```

Convert ADF to plain text (strips formatting).

**Example:**
```python
from confluence_assistant_skills import adf_to_text

text = adf_to_text(adf)
# "Hello World" (no formatting marks)
```

## Node Creation Functions

For programmatic ADF construction:

### create_adf_doc()

```python
def create_adf_doc(content: list[dict]) -> dict
```

Create an ADF document wrapper.

**Example:**
```python
from confluence_assistant_skills import (
    create_adf_doc,
    create_paragraph,
    create_heading,
)

doc = create_adf_doc([
    create_heading("Title", level=1),
    create_paragraph(text="Content here."),
])
```

### create_paragraph()

```python
def create_paragraph(
    content: list[dict] = None,
    text: str = None
) -> dict
```

Create an ADF paragraph node.

**Example:**
```python
# Simple text
para = create_paragraph(text="Hello, world!")

# With inline nodes
para = create_paragraph(content=[
    create_text("Hello, "),
    create_text("world!", marks=[{"type": "strong"}])
])
```

### create_text()

```python
def create_text(text: str, marks: list[dict] = None) -> dict
```

Create an ADF text node with optional marks.

**Marks:**
- `{"type": "strong"}` - bold
- `{"type": "em"}` - italic
- `{"type": "code"}` - inline code
- `{"type": "link", "attrs": {"href": "..."}}` - link
- `{"type": "strike"}` - strikethrough

**Example:**
```python
bold = create_text("Important", marks=[{"type": "strong"}])
link = create_text("Click here", marks=[
    {"type": "link", "attrs": {"href": "https://example.com"}}
])
```

### create_heading()

```python
def create_heading(text: str, level: int = 1) -> dict
```

Create an ADF heading node.

**Example:**
```python
h1 = create_heading("Main Title", level=1)
h2 = create_heading("Subsection", level=2)
```

### create_bullet_list()

```python
def create_bullet_list(items: list[str]) -> dict
```

Create an ADF bullet list.

**Example:**
```python
ul = create_bullet_list(["First item", "Second item", "Third item"])
```

### create_ordered_list()

```python
def create_ordered_list(items: list[str], start: int = 1) -> dict
```

Create an ADF ordered list.

**Example:**
```python
ol = create_ordered_list(["Step one", "Step two", "Step three"])
ol_from_five = create_ordered_list(["Continue", "Finish"], start=5)
```

### create_code_block()

```python
def create_code_block(code: str, language: str = None) -> dict
```

Create an ADF code block.

**Example:**
```python
code = create_code_block("print('Hello')", language="python")
```

### create_blockquote()

```python
def create_blockquote(text: str) -> dict
```

Create an ADF blockquote.

**Example:**
```python
quote = create_blockquote("To be or not to be.")
```

### create_rule()

```python
def create_rule() -> dict
```

Create an ADF horizontal rule.

### create_table()

```python
def create_table(rows: list[list[str]], header: bool = True) -> dict
```

Create an ADF table.

**Example:**
```python
table = create_table([
    ["Name", "Age", "City"],      # Header row
    ["Alice", "30", "NYC"],
    ["Bob", "25", "LA"],
])
```

### create_link()

```python
def create_link(text: str, url: str) -> dict
```

Create an ADF text node with link mark.

**Example:**
```python
link = create_link("Visit site", "https://example.com")
```

## Validation

### validate_adf()

```python
def validate_adf(adf: dict) -> bool
```

Validate basic ADF structure.

**Example:**
```python
from confluence_assistant_skills import validate_adf

try:
    validate_adf(adf)
except ValueError as e:
    print(f"Invalid ADF: {e}")
```

**Checks:**
- Must be a dictionary
- Must have `type: "doc"`
- Must have `content` array
