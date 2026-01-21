# Validators

Input validation functions that raise `ValidationError` on failure.

## Page and Content

### validate_page_id()

```python
def validate_page_id(page_id: str | int, field_name: str = "page_id") -> str
```

Validate a Confluence page ID (must be numeric).

**Example:**
```python
from confluence_as import validate_page_id, ValidationError

try:
    page_id = validate_page_id("12345")  # Returns "12345"
    page_id = validate_page_id(12345)    # Also works with int
except ValidationError as e:
    print(f"Invalid page ID: {e}")
```

### validate_space_key()

```python
def validate_space_key(
    space_key: str,
    field_name: str = "space_key",
    allow_lowercase: bool = True
) -> str
```

Validate a Confluence space key. Returns uppercase by default.

**Example:**
```python
from confluence_as import validate_space_key

space = validate_space_key("docs")   # Returns "DOCS"
space = validate_space_key("DOCS")   # Returns "DOCS"
```

**Rules:**
- 2-255 characters
- Must start with a letter
- Only letters, numbers, and underscores allowed

### validate_content_type()

```python
def validate_content_type(
    content_type: str,
    field_name: str = "content_type",
    allowed_types: list = None
) -> str
```

Validate content type (page, blogpost, comment, attachment).

**Example:**
```python
from confluence_as import validate_content_type

content_type = validate_content_type("page")      # Returns "page"
content_type = validate_content_type("blogpost")  # Returns "blogpost"
```

### validate_title()

```python
def validate_title(title: str, field_name: str = "title") -> str
```

Validate a page title.

**Rules:**
- 1-255 characters
- Cannot contain certain special characters

## Queries

### validate_cql()

```python
def validate_cql(cql: str, field_name: str = "cql") -> str
```

Validate a CQL (Confluence Query Language) query.

**Example:**
```python
from confluence_as import validate_cql

# Valid queries
cql = validate_cql('space = "DOCS" AND type = page')
cql = validate_cql('label = "important" ORDER BY created DESC')

# Invalid - unbalanced quotes
validate_cql('space = "DOCS')  # Raises ValidationError
```

**Checks:**
- Required (non-empty)
- Balanced quotes and parentheses

### validate_jql_query()

```python
def validate_jql_query(jql: str, field_name: str = "jql") -> str
```

Validate a JQL (JIRA Query Language) query.

Similar to `validate_cql()` but for JIRA queries.

## URLs and Paths

### validate_url()

```python
def validate_url(url: str, field_name: str = "url") -> str
```

Validate a URL.

**Example:**
```python
from confluence_as import validate_url

url = validate_url("https://example.com/path")
```

### validate_email()

```python
def validate_email(email: str, field_name: str = "email") -> str
```

Validate an email address.

**Example:**
```python
from confluence_as import validate_email

email = validate_email("user@example.com")
```

### validate_file_path()

```python
def validate_file_path(
    path: str | Path,
    field_name: str = "file_path",
    must_exist: bool = True
) -> Path
```

Validate a file path.

**Example:**
```python
from confluence_as import validate_file_path

path = validate_file_path("/path/to/file.pdf")
path = validate_file_path("file.txt", must_exist=False)  # Doesn't check existence
```

## Labels and JIRA

### validate_label()

```python
def validate_label(label: str, field_name: str = "label") -> str
```

Validate a Confluence label.

**Rules:**
- Must be non-empty
- Only alphanumeric, dash, underscore allowed
- No spaces

### validate_issue_key()

```python
def validate_issue_key(issue_key: str, field_name: str = "issue_key") -> str
```

Validate a JIRA issue key (e.g., "PROJ-123").

**Example:**
```python
from confluence_as import validate_issue_key

key = validate_issue_key("PROJ-123")   # Returns "PROJ-123"
key = validate_issue_key("ABC-1")      # Returns "ABC-1"
```

## Pagination

### validate_limit()

```python
def validate_limit(
    limit: int | str,
    field_name: str = "limit",
    min_value: int = 1,
    max_value: int = 250
) -> int
```

Validate a pagination limit.

**Example:**
```python
from confluence_as import validate_limit

limit = validate_limit(25)      # Returns 25
limit = validate_limit("100")   # Returns 100
limit = validate_limit(500)     # Raises ValidationError (> max)
```

## Error Handling

All validators raise `ValidationError` on failure:

```python
from confluence_as import validate_page_id, ValidationError

try:
    validate_page_id("not-a-number")
except ValidationError as e:
    print(f"Error: {e.message}")
    print(f"Details: {e.details}")
```
