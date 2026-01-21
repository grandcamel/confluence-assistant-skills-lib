# Client API

The `ConfluenceClient` class provides HTTP access to the Confluence Cloud REST API.

## ConfluenceClient

```python
from confluence_as import ConfluenceClient

client = ConfluenceClient(
    base_url="https://your-site.atlassian.net",
    email="your-email@example.com",
    api_token="your-api-token",
)
```

### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | str | required | Confluence Cloud URL |
| `email` | str | required | User email for authentication |
| `api_token` | str | required | API token |
| `timeout` | int | 30 | Request timeout in seconds |
| `max_retries` | int | 3 | Max retry attempts for 429/5xx |
| `retry_backoff` | float | 2.0 | Exponential backoff multiplier |
| `verify_ssl` | bool | True | Verify SSL certificates |

## HTTP Methods

### get()

```python
def get(
    endpoint: str,
    params: dict = None,
    operation: str = "GET request"
) -> dict
```

Perform a GET request.

**Example:**
```python
# Get a page by ID
page = client.get("/api/v2/pages/12345")

# Get pages in a space
pages = client.get("/api/v2/pages", params={"space-id": "123456"})
```

### post()

```python
def post(
    endpoint: str,
    data: dict = None,
    json_data: dict | list = None,
    params: dict = None,
    operation: str = "POST request"
) -> dict
```

Perform a POST request with JSON body.

**Example:**
```python
# Create a new page
new_page = client.post("/api/v2/pages", json_data={
    "spaceId": "123456",
    "title": "New Page",
    "body": {
        "representation": "storage",
        "value": "<p>Page content</p>"
    }
})
```

### put()

```python
def put(
    endpoint: str,
    data: dict = None,
    json_data: dict | list = None,
    params: dict = None,
    operation: str = "PUT request"
) -> dict
```

Perform a PUT request with JSON body.

**Example:**
```python
# Update a page
updated = client.put(f"/api/v2/pages/{page_id}", json_data={
    "id": page_id,
    "title": "Updated Title",
    "body": {
        "representation": "storage",
        "value": "<p>Updated content</p>"
    },
    "version": {"number": 2}
})
```

### delete()

```python
def delete(
    endpoint: str,
    params: dict = None,
    operation: str = "DELETE request"
) -> dict
```

Perform a DELETE request.

**Example:**
```python
# Delete a page
client.delete(f"/api/v2/pages/{page_id}")
```

## Pagination

### paginate()

```python
def paginate(
    endpoint: str,
    params: dict = None,
    operation: str = "paginated request",
    limit: int = None,
    results_key: str = "results"
) -> Generator
```

Generator that handles cursor-based pagination automatically.

**Example:**
```python
# Iterate through all pages in a space
for page in client.paginate("/api/v2/pages", params={"space-id": "123456"}):
    print(page["title"])

# Limit results
for page in client.paginate("/api/v2/pages", limit=10):
    print(page["title"])

# Collect all results
all_pages = list(client.paginate("/api/v2/pages"))
```

## File Operations

### upload_file()

```python
def upload_file(
    endpoint: str,
    file_path: str | Path,
    params: dict = None,
    additional_data: dict = None,
    operation: str = "upload file"
) -> dict
```

Upload a file to Confluence.

### upload_attachment()

```python
def upload_attachment(
    page_id: str,
    file_path: str | Path,
    comment: str = None,
    operation: str = "upload attachment"
) -> dict
```

Upload an attachment to a page.

**Example:**
```python
result = client.upload_attachment(
    page_id="12345",
    file_path="/path/to/document.pdf",
    comment="Initial upload"
)
print(f"Attachment ID: {result['results'][0]['id']}")
```

### download_attachment()

```python
def download_attachment(
    attachment_id: str,
    operation: str = "download attachment"
) -> bytes
```

Download an attachment's content.

**Example:**
```python
content = client.download_attachment("att123456")
with open("downloaded.pdf", "wb") as f:
    f.write(content)
```

### download_file()

```python
def download_file(
    download_url: str,
    output_path: str | Path,
    operation: str = "download file"
) -> Path
```

Download a file to a local path.

**Example:**
```python
path = client.download_file(
    "/wiki/download/attachments/12345/file.pdf",
    "/local/path/file.pdf"
)
```

### update_attachment()

```python
def update_attachment(
    attachment_id: str,
    page_id: str,
    file_path: str | Path,
    comment: str = None,
    operation: str = "update attachment"
) -> dict
```

Replace an existing attachment with a new file.

## Connection Testing

### test_connection()

```python
def test_connection() -> dict
```

Test the connection to Confluence.

**Example:**
```python
result = client.test_connection()
if result["success"]:
    print(f"Connected as: {result['user']}")
else:
    print(f"Connection failed: {result['error']}")
```

## Factory Functions

### get_confluence_client()

```python
from confluence_as import get_confluence_client

# Uses environment variables for configuration
client = get_confluence_client()
```

Creates a client using environment variables:
- `CONFLUENCE_SITE_URL`
- `CONFLUENCE_EMAIL`
- `CONFLUENCE_API_TOKEN`

### create_client()

```python
from confluence_as import create_client

client = create_client(
    base_url="https://your-site.atlassian.net",
    email="email@example.com",
    api_token="token",
    timeout=60
)
```

Factory function for creating clients with custom options.
