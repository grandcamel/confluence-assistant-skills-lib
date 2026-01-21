# Error Handling

Exception hierarchy for Confluence API errors.

## Exception Hierarchy

```
ConfluenceError (base for all Confluence errors)
├── AuthenticationError (401)
├── PermissionError (403)
├── ValidationError (400)
├── NotFoundError (404)
├── RateLimitError (429)
├── ConflictError (409)
└── ServerError (5xx)
```

## Exception Classes

### ConfluenceError

Base exception for all Confluence-related errors.

```python
from confluence_as import ConfluenceError

try:
    client.get("/api/v2/pages/invalid")
except ConfluenceError as e:
    print(f"Error: {e.message}")
    print(f"Status: {e.status_code}")
    print(f"Operation: {e.operation}")
```

**Attributes:**
- `message` - Error message
- `status_code` - HTTP status code
- `response_data` - Raw response text
- `operation` - Description of the failed operation

### AuthenticationError

Raised when authentication fails (HTTP 401).

```python
from confluence_as import AuthenticationError

try:
    client.get("/api/v2/pages/12345")
except AuthenticationError:
    print("Check your email and API token")
```

### PermissionError

Raised when user lacks permission (HTTP 403).

```python
from confluence_as import PermissionError

try:
    client.delete(f"/api/v2/pages/{page_id}")
except PermissionError as e:
    print(f"Access denied: {e.message}")
```

### ValidationError

Raised for invalid input or bad requests (HTTP 400).

Also raised by validators when input fails validation.

```python
from confluence_as import ValidationError, validate_page_id

try:
    validate_page_id("not-a-number")
except ValidationError as e:
    print(f"Invalid input: {e.message}")
```

### NotFoundError

Raised when a resource is not found (HTTP 404).

```python
from confluence_as import NotFoundError

try:
    client.get("/api/v2/pages/99999999")
except NotFoundError:
    print("Page does not exist")
```

### RateLimitError

Raised when rate limit is exceeded (HTTP 429).

```python
from confluence_as import RateLimitError

try:
    for page_id in page_ids:
        client.get(f"/api/v2/pages/{page_id}")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after} seconds")
```

**Additional Attributes:**
- `retry_after` - Seconds to wait before retrying (from `Retry-After` header)

### ConflictError

Raised on resource conflicts (HTTP 409), such as version conflicts during updates.

```python
from confluence_as import ConflictError

try:
    client.put(f"/api/v2/pages/{page_id}", json_data=update_data)
except ConflictError:
    print("Page was modified by another user. Refresh and try again.")
```

### ServerError

Raised for server-side errors (HTTP 5xx).

```python
from confluence_as import ServerError

try:
    client.get("/api/v2/pages")
except ServerError:
    print("Confluence server error. Try again later.")
```

## Error Handling Utilities

### handle_confluence_error()

```python
def handle_confluence_error(response: Response, operation: str = "API request") -> None
```

Convert an HTTP error response to the appropriate exception.

```python
from confluence_as import handle_confluence_error

response = requests.get(url, headers=headers)
if not response.ok:
    handle_confluence_error(response, "get page")  # Raises appropriate exception
```

### handle_errors decorator

```python
@handle_errors
def main():
    client = get_confluence_client()
    # ... your code
```

Decorator that catches exceptions and prints formatted error messages.

### print_error()

```python
def print_error(
    message: str,
    error: Exception = None,
    suggestion: str = None,
    show_traceback: bool = False
) -> None
```

Print a formatted error message to stderr.

```python
from confluence_as import print_error

try:
    client.get("/api/v2/pages/12345")
except ConfluenceError as e:
    print_error("Failed to get page", e, suggestion="Check if page exists")
```

### extract_error_message()

```python
def extract_error_message(response: Response) -> str
```

Extract a meaningful error message from a Confluence API response.

### sanitize_error_message()

```python
def sanitize_error_message(message: str) -> str
```

Sanitize error messages (e.g., remove sensitive data).

## ErrorContext

Context manager for adding context to errors.

```python
from confluence_as import ErrorContext

with ErrorContext("updating page", page_id="12345", title="My Page"):
    client.put(f"/api/v2/pages/12345", json_data=data)
# If error occurs, exception includes context: "updating page (page_id=12345, title=My Page)"
```

## Catching Multiple Error Types

```python
from confluence_as import (
    ConfluenceError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)

try:
    page = client.get(f"/api/v2/pages/{page_id}")
except AuthenticationError:
    print("Please check your credentials")
    sys.exit(1)
except NotFoundError:
    print(f"Page {page_id} not found")
except RateLimitError as e:
    time.sleep(e.retry_after or 60)
    page = client.get(f"/api/v2/pages/{page_id}")  # Retry
except ConfluenceError as e:
    print(f"Confluence error: {e.message}")
```
