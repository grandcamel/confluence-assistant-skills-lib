# Examples

Practical examples for common Confluence operations.

## Setup

All examples assume you have configured credentials:

```bash
export CONFLUENCE_SITE_URL=https://your-site.atlassian.net
export CONFLUENCE_EMAIL=your-email@example.com
export CONFLUENCE_API_TOKEN=your-api-token
```

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()
```

## Page Operations

### Get a Page

```python
from confluence_assistant_skills import (
    get_confluence_client,
    validate_page_id,
    format_page,
)

client = get_confluence_client()

page_id = validate_page_id("12345")
page = client.get(f"/api/v2/pages/{page_id}")
print(format_page(page, detailed=True))
```

### Create a Page

```python
import json
from confluence_assistant_skills import (
    get_confluence_client,
    markdown_to_adf,
)

client = get_confluence_client()

content = """
# Welcome

This is the page content with **bold** and *italic* text.

## Features

- Feature one
- Feature two
- Feature three
"""

adf = markdown_to_adf(content)

new_page = client.post("/api/v2/pages", json_data={
    "spaceId": "123456",
    "title": "My New Page",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(adf)
    }
})

print(f"Created page: {new_page['id']}")
```

### Update a Page

```python
import json
from confluence_assistant_skills import (
    get_confluence_client,
    markdown_to_adf,
)

client = get_confluence_client()
page_id = "12345"

# Get current version
page = client.get(f"/api/v2/pages/{page_id}")
current_version = page["version"]["number"]

# Update with new content
new_content = markdown_to_adf("# Updated Content\n\nNew paragraph.")

updated = client.put(f"/api/v2/pages/{page_id}", json_data={
    "id": page_id,
    "title": "Updated Title",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(new_content)
    },
    "version": {"number": current_version + 1}
})

print(f"Updated to version {updated['version']['number']}")
```

### Delete a Page

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()
client.delete("/api/v2/pages/12345")
print("Page deleted")
```

## Search and CQL

### Search with CQL

```python
from confluence_assistant_skills import (
    get_confluence_client,
    validate_cql,
    format_search_results,
)

client = get_confluence_client()

cql = validate_cql('space = "DOCS" AND type = page AND label = "important"')
response = client.get("/rest/api/content/search", params={"cql": cql})
print(format_search_results(response["results"], show_excerpt=True))
```

### Find Pages in a Space

```python
from confluence_assistant_skills import (
    get_confluence_client,
    format_table,
)

client = get_confluence_client()

# Get space ID first
space = client.get("/api/v2/spaces", params={"keys": "DOCS"})
space_id = space["results"][0]["id"]

# Get all pages
pages = list(client.paginate(f"/api/v2/spaces/{space_id}/pages"))

table = format_table(
    pages,
    columns=["id", "title", "status"],
    headers=["ID", "Title", "Status"]
)
print(table)
```

## Bulk Operations

### Export All Pages to CSV

```python
from confluence_assistant_skills import (
    get_confluence_client,
    export_csv,
)

client = get_confluence_client()

pages = list(client.paginate("/api/v2/pages", params={"space-id": "123456"}))

export_csv(
    pages,
    "pages.csv",
    columns=["id", "title", "status", "createdAt"]
)
print(f"Exported {len(pages)} pages to pages.csv")
```

### Bulk Update Labels

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

page_ids = ["12345", "67890", "11111"]
label = "reviewed"

for page_id in page_ids:
    client.post(f"/api/v2/pages/{page_id}/labels", json_data={
        "label": label
    })
    print(f"Added label '{label}' to page {page_id}")
```

## Content Conversion

### Markdown to ADF

```python
import json
from confluence_assistant_skills import markdown_to_adf, validate_adf

markdown = """
# Project Status

**Status:** Active

## Tasks

1. Complete documentation
2. Add tests
3. Deploy

> Important: Review before merge.

```python
print("Hello, World!")
```
"""

adf = markdown_to_adf(markdown)
validate_adf(adf)  # Raises ValueError if invalid
print(json.dumps(adf, indent=2))
```

### Read Page Content as Markdown

```python
import json
from confluence_assistant_skills import (
    get_confluence_client,
    adf_to_markdown,
)

client = get_confluence_client()

page = client.get("/api/v2/pages/12345?body-format=atlas_doc_format")
adf = json.loads(page["body"]["atlas_doc_format"]["value"])
markdown = adf_to_markdown(adf)
print(markdown)
```

### Migrate V1 to V2 Content

```python
import json
from confluence_assistant_skills import (
    get_confluence_client,
    xhtml_to_adf,
)

client = get_confluence_client()

# Get page from v1 API
v1_page = client.get("/rest/api/content/12345?expand=body.storage")
xhtml = v1_page["body"]["storage"]["value"]

# Convert to ADF
adf = xhtml_to_adf(xhtml)

# Update using v2 API
client.put("/api/v2/pages/12345", json_data={
    "id": "12345",
    "title": v1_page["title"],
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(adf)
    },
    "version": {"number": v1_page["version"]["number"] + 1}
})
```

## File Attachments

### Upload Attachment

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

result = client.upload_attachment(
    page_id="12345",
    file_path="/path/to/document.pdf",
    comment="Initial upload"
)
print(f"Attachment ID: {result['results'][0]['id']}")
```

### Download Attachment

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

content = client.download_attachment("att123456")
with open("downloaded.pdf", "wb") as f:
    f.write(content)
print("Downloaded attachment")
```

### List Page Attachments

```python
from confluence_assistant_skills import (
    get_confluence_client,
    format_attachment,
)

client = get_confluence_client()

attachments = list(client.paginate("/api/v2/pages/12345/attachments"))
for att in attachments:
    print(format_attachment(att))
```

## Comments

### Get Page Comments

```python
from confluence_assistant_skills import (
    get_confluence_client,
    format_comments,
)

client = get_confluence_client()

comments = list(client.paginate("/api/v2/pages/12345/footer-comments"))
print(format_comments(comments))
```

### Add Comment to Page

```python
import json
from confluence_assistant_skills import (
    get_confluence_client,
    text_to_adf,
)

client = get_confluence_client()

comment_body = text_to_adf("This looks good! Approved.")

client.post("/api/v2/footer-comments", json_data={
    "pageId": "12345",
    "body": {
        "representation": "atlas_doc_format",
        "value": json.dumps(comment_body)
    }
})
print("Comment added")
```

## Error Handling

### Graceful Error Handling

```python
from confluence_assistant_skills import (
    get_confluence_client,
    ConfluenceError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
)
import time

client = get_confluence_client()

def get_page_safe(page_id: str):
    try:
        return client.get(f"/api/v2/pages/{page_id}")
    except AuthenticationError:
        print("Authentication failed. Check credentials.")
        return None
    except NotFoundError:
        print(f"Page {page_id} not found")
        return None
    except RateLimitError as e:
        print(f"Rate limited. Waiting {e.retry_after}s...")
        time.sleep(e.retry_after or 60)
        return client.get(f"/api/v2/pages/{page_id}")
    except ConfluenceError as e:
        print(f"Error: {e.message}")
        return None

page = get_page_safe("12345")
if page:
    print(f"Found: {page['title']}")
```

### Using ErrorContext

```python
from confluence_assistant_skills import (
    get_confluence_client,
    ErrorContext,
    ConfluenceError,
)

client = get_confluence_client()

def update_page(page_id: str, title: str, content: str):
    with ErrorContext("updating page", page_id=page_id, title=title):
        page = client.get(f"/api/v2/pages/{page_id}")
        client.put(f"/api/v2/pages/{page_id}", json_data={
            "id": page_id,
            "title": title,
            "body": {"representation": "storage", "value": content},
            "version": {"number": page["version"]["number"] + 1}
        })

try:
    update_page("12345", "New Title", "<p>Content</p>")
except ConfluenceError as e:
    print(f"Failed: {e.operation}")  # "updating page (page_id=12345, title=New Title)"
```

## Pagination

### Iterate All Results

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

# Automatically handles cursor-based pagination
for page in client.paginate("/api/v2/pages"):
    print(page["title"])
```

### Limit Results

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

# Stop after 100 results
pages = list(client.paginate("/api/v2/pages", limit=100))
print(f"Got {len(pages)} pages")
```

### Collect All Results

```python
from confluence_assistant_skills import get_confluence_client

client = get_confluence_client()

all_spaces = list(client.paginate("/api/v2/spaces"))
print(f"Total spaces: {len(all_spaces)}")
```
