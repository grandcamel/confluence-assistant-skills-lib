# Formatters

Output formatting utilities for Confluence data.

## Page Formatting

### format_page()

```python
def format_page(page: dict, detailed: bool = False) -> str
```

Format a page for display.

**Example:**
```python
from confluence_assistant_skills import format_page

page = client.get("/api/v2/pages/12345")
print(format_page(page))
# Output: Test Page (ID: 12345) [current] - Space: 123

print(format_page(page, detailed=True))
# Includes labels, version info, etc.
```

### format_blogpost()

```python
def format_blogpost(blogpost: dict, detailed: bool = False) -> str
```

Format a blog post for display.

### format_space()

```python
def format_space(space: dict, detailed: bool = False) -> str
```

Format a space for display.

**Example:**
```python
from confluence_assistant_skills import format_space

spaces = list(client.paginate("/api/v2/spaces"))
for space in spaces:
    print(format_space(space))
```

## Comments

### format_comment()

```python
def format_comment(comment: dict, show_body: bool = False) -> str
```

Format a single comment.

### format_comments()

```python
def format_comments(comments: list, limit: int = None) -> str
```

Format a list of comments.

**Example:**
```python
from confluence_assistant_skills import format_comments

comments = list(client.paginate(f"/api/v2/pages/{page_id}/footer-comments"))
print(format_comments(comments, limit=5))
```

## Search Results

### format_search_results()

```python
def format_search_results(
    results: list,
    show_excerpt: bool = False,
    show_labels: bool = False
) -> str
```

Format search results for display.

**Example:**
```python
from confluence_assistant_skills import format_search_results

response = client.get("/rest/api/content/search", params={"cql": "space=DOCS"})
print(format_search_results(response["results"], show_excerpt=True))
```

## Tables

### format_table()

```python
def format_table(
    data: list[dict],
    columns: list[str],
    headers: list[str] = None,
    max_width: int = None
) -> str
```

Format data as an ASCII table.

**Example:**
```python
from confluence_assistant_skills import format_table

pages = [
    {"id": "1", "title": "Home", "status": "current"},
    {"id": "2", "title": "About", "status": "draft"},
]

table = format_table(
    pages,
    columns=["id", "title", "status"],
    headers=["ID", "Title", "Status"]
)
print(table)
# +----+-------+---------+
# | ID | Title | Status  |
# +----+-------+---------+
# | 1  | Home  | current |
# | 2  | About | draft   |
# +----+-------+---------+
```

## JSON and CSV

### format_json()

```python
def format_json(data: Any, indent: int = 2) -> str
```

Format data as pretty-printed JSON.

**Example:**
```python
from confluence_assistant_skills import format_json

page = client.get("/api/v2/pages/12345")
print(format_json(page))
```

### export_csv()

```python
def export_csv(
    data: list[dict],
    output_path: str | Path,
    columns: list[str] = None
) -> Path
```

Export data to a CSV file.

**Example:**
```python
from confluence_assistant_skills import export_csv

pages = list(client.paginate("/api/v2/pages", params={"space-id": "123"}))
export_csv(pages, "pages.csv", columns=["id", "title", "status"])
```

## Attachments and Labels

### format_attachment()

```python
def format_attachment(attachment: dict) -> str
```

Format an attachment for display.

### format_label()

```python
def format_label(label: dict) -> str
```

Format a label for display.

### format_version()

```python
def format_version(version: dict) -> str
```

Format version information.

## Timestamps

### format_timestamp()

```python
def format_timestamp(
    timestamp: str,
    format_str: str = "%Y-%m-%d %H:%M:%S"
) -> str
```

Format an ISO timestamp.

**Example:**
```python
from confluence_assistant_skills import format_timestamp

ts = format_timestamp("2024-01-15T10:30:00Z")
# Returns: "2024-01-15 10:30:00"

ts = format_timestamp("2024-01-15T10:30:00Z", format_str="%B %d, %Y")
# Returns: "January 15, 2024"
```

## Text Utilities

### truncate()

```python
def truncate(text: str, max_length: int = 80, suffix: str = "...") -> str
```

Truncate text to a maximum length.

**Example:**
```python
from confluence_assistant_skills import truncate

text = truncate("This is a very long text", max_length=15)
# Returns: "This is a ve..."
```

### strip_html_tags()

```python
def strip_html_tags(html: str, collapse_whitespace: bool = True) -> str
```

Remove HTML tags from text.

**Example:**
```python
from confluence_assistant_skills import strip_html_tags

text = strip_html_tags("<p>Hello <strong>World</strong></p>")
# Returns: "Hello World"
```

## Console Output

### print_success()

```python
def print_success(message: str) -> None
```

Print a success message (green).

### print_warning()

```python
def print_warning(message: str) -> None
```

Print a warning message (yellow).

### print_info()

```python
def print_info(message: str) -> None
```

Print an info message (blue).

**Example:**
```python
from confluence_assistant_skills import print_success, print_warning

print_success("Page created successfully!")
print_warning("Some content was skipped")
```
