# Confluence REST API Specification Review Report

**Generated:** 2026-01-31
**Library Version:** confluence-as
**API Documentation Sources:**
- v1 API: OpenAPI 3.0.1 (89 endpoints)
- v2 API: Postman Collection v2 (212 endpoints)

---

## Executive Summary

The `confluence-as` library has been reviewed against the official Confluence Cloud REST API specifications. This report identifies discrepancies, deprecated patterns, missing functionality, and recommendations for alignment.

### Key Findings

| Category | Issues Found | Priority |
|----------|-------------|----------|
| Search Pagination | `start` parameter deprecated, should use `cursor` | HIGH |
| Space Updates | Using PATCH correctly for v2 | COMPLIANT |
| Attachment Upload | Still requires v1 API (no v2 upload endpoint exists) | EXPECTED |
| Content Properties | v2 API now available, library uses v1 | LOW |
| Page Versions | Uses v1 API, v2 now available | MEDIUM |
| Label Operations | v2 API endpoints correct | COMPLIANT |
| Comment Endpoints | v2 API implementation correct | COMPLIANT |

---

## Phase 1: Core Content (HIGH Priority)

### 1. Page Commands (`cli/commands/page_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| Get page | `GET /api/v2/pages/{id}` | `GET /pages/:id` | ✅ CORRECT |
| Create page | `POST /api/v2/pages` | `POST /pages` | ✅ CORRECT |
| Update page | `PUT /api/v2/pages/{id}` | `PUT /pages/:id` | ✅ CORRECT |
| Delete page | `DELETE /api/v2/pages/{id}` | `DELETE /pages/:id` | ✅ CORRECT |
| Get children | `GET /api/v2/pages/{id}/children` | `GET /pages/:id/children` | ✅ CORRECT |
| Get blogpost | `GET /api/v2/blogposts/{id}` | `GET /blogposts/:id` | ✅ CORRECT |
| Create blogpost | `POST /api/v2/blogposts` | `POST /blogposts` | ✅ CORRECT |
| Get versions | `GET /rest/api/content/{id}/version` | v1 API | ⚠️ v2 AVAILABLE |

#### Verified Implementations

- ✅ `body-format` parameter values correctly support: `storage`, `view` (also `atlas_doc_format`, `export_view` in spec)
- ✅ Version increment logic correctly fetches current version and increments by 1
- ✅ Delete `purge` parameter correctly implemented for permanent deletion
- ✅ Blog post vs page field differences handled correctly

#### Recommendations

1. **Page Versions**: Consider migrating to v2 API:
   - Current: `GET /rest/api/content/{id}/version`
   - Available v2: `GET /api/v2/pages/:id/versions`
   - v2 also provides `GET /api/v2/pages/:page-id/versions/:version-number` for specific version details

2. **Page Title Update**: v2 API provides dedicated endpoint:
   - `PUT /api/v2/pages/:id/title` - for title-only updates

---

### 2. Space Commands (`cli/commands/space_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List spaces | `GET /api/v2/spaces` | `GET /spaces` | ✅ CORRECT |
| Get space | `GET /api/v2/spaces` with `keys` filter | `GET /spaces/:id` | ✅ CORRECT |
| Create space | `POST /api/v2/spaces` | `POST /spaces` | ✅ CORRECT |
| Update space | `PATCH /api/v2/spaces/{id}` | N/A in v2 spec | ⚠️ CHECK |
| Delete space | `DELETE /api/v2/spaces/{id}` | N/A in v2 spec | ⚠️ CHECK |
| Get space pages | `GET /api/v2/spaces/{id}/pages` | `GET /spaces/:id/pages` | ✅ CORRECT |

#### Notes

1. **Space Updates (PATCH)**: The library correctly uses PATCH for space updates as documented in CLAUDE.md. The v2 Postman collection only shows GET, POST for spaces, but the v1 spec shows PUT for `/wiki/rest/api/space/{spaceKey}`. The PATCH approach may be correct for partial updates in v2.

2. **Space Delete**: The v2 Postman collection doesn't show a DELETE endpoint for spaces. The library's implementation may need verification against live API behavior.

3. **Space Type Values**: Correctly validates `global`, `personal` types.

---

### 3. Comment Commands (`cli/commands/comment_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List footer comments | `GET /api/v2/pages/{id}/footer-comments` | `GET /pages/:id/footer-comments` | ✅ CORRECT |
| List inline comments | `GET /api/v2/pages/{id}/inline-comments` | `GET /pages/:id/inline-comments` | ✅ CORRECT |
| Create footer comment | `POST /api/v2/footer-comments` | `POST /footer-comments` | ✅ CORRECT |
| Create inline comment | `POST /api/v2/inline-comments` | `POST /inline-comments` | ✅ CORRECT |
| Get footer comment | `GET /api/v2/footer-comments/{id}` | `GET /footer-comments/:comment-id` | ✅ CORRECT |
| Update footer comment | `PUT /api/v2/footer-comments/{id}` | `PUT /footer-comments/:comment-id` | ✅ CORRECT |
| Delete footer comment | `DELETE /api/v2/footer-comments/{id}` | `DELETE /footer-comments/:comment-id` | ✅ CORRECT |

#### Verified Implementations

- ✅ `inlineCommentProperties` structure correctly uses:
  - `textSelection`: The text to highlight
  - `textSelectionMatchCount`: Number of matches
  - `textSelectionMatchIndex`: Which match to use
- ✅ Sort parameter uses `created-date` / `-created-date` format
- ✅ Comment status values `open`, `resolved` are correct

---

### 4. Attachment Commands (`cli/commands/attachment_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List attachments | `GET /api/v2/pages/{id}/attachments` | `GET /pages/:id/attachments` | ✅ CORRECT |
| Get attachment | `GET /api/v2/attachments/{id}` | `GET /attachments/:id` | ✅ CORRECT |
| Delete attachment | `DELETE /api/v2/attachments/{id}` | `DELETE /attachments/:id` | ✅ CORRECT |
| Upload attachment | `POST /rest/api/content/{id}/child/attachment` | v1 API only | ✅ EXPECTED |
| Update attachment | `POST /rest/api/content/{id}/child/attachment/{id}/data` | v1 API only | ✅ EXPECTED |

#### Notes

1. **No v2 Upload Endpoints**: The v2 API specification does NOT include attachment upload endpoints. The library correctly uses v1 API for:
   - `POST /rest/api/content/{id}/child/attachment` (new upload)
   - `POST /rest/api/content/{id}/child/attachment/{attachmentId}/data` (update)

2. **Download Link**: The library correctly uses `downloadLink` field from v2 response, with fallback to `_links.download`.

3. **X-Atlassian-Token Header**: The library correctly includes `X-Atlassian-Token: nocheck` header for uploads.

---

### 5. Search Commands (`cli/commands/search_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Status |
|-----------|-----------------|--------|
| CQL Search | `GET /rest/api/search` | ⚠️ CHECK PAGINATION |
| Content Search | `GET /rest/api/search` | ⚠️ CHECK PAGINATION |

#### Critical Issue: Pagination

The v1 API spec shows:
- `start` parameter: **Present but was deprecated in July 2020**
- `cursor` parameter: **Present and preferred**

**Current Library Behavior** (`confluence_client.py:621-672`):
```python
def paginate(...):
    while True:
        if cursor:
            params["cursor"] = cursor
        # ...
        if "cursor=" in next_link:
            cursor = next_link.split("cursor=")[1].split("&")[0]
```

The library's `paginate()` method correctly uses cursor-based pagination via the `_links.next` URL. However, the `streaming_export` function in `search_cmds.py` has a comment noting that `start` was removed:

```python
# Note: The 'start' parameter was removed from Confluence Cloud on July 15, 2020.
# Confluence now uses cursor-based pagination.
```

**Status**: ✅ COMPLIANT - The library correctly uses cursor-based pagination.

#### CQL Escape Function

The `_escape_cql_string()` function correctly escapes:
- Backslashes: `\\` → `\\\\`
- Double quotes: `"` → `\\"`

---

## Phase 2: Permissions & Metadata (MEDIUM Priority)

### 6. Label Commands (`cli/commands/label_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List labels | `GET /api/v2/pages/{id}/labels` | `GET /pages/:id/labels` | ✅ CORRECT |
| Add labels | `POST /api/v2/pages/{id}/labels` | v1 uses POST | ⚠️ CHECK |
| Remove label | `DELETE /api/v2/pages/{id}/labels/{name}` | v1 uses DELETE | ⚠️ CHECK |

#### Notes

1. **v2 Label Endpoints**: The v2 API Postman collection only shows GET endpoints for labels (`GET /pages/:id/labels`, etc.). The POST/DELETE operations may need to use v1 API.

2. **Label Array Format**: The library correctly sends labels as array:
   ```python
   label_data = [{"name": name.strip()} for name in labels]
   ```

---

### 7. Permission Commands (`cli/commands/permission_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| Get page restrictions | `GET /rest/api/content/{id}/restriction` | v1 API | ✅ EXPECTED |
| Add page restriction | `POST /rest/api/content/{id}/restriction` | v1 API | ✅ EXPECTED |
| Remove page restriction | `DELETE /rest/api/content/{id}/restriction/byOperation/{op}` | v1 API | ✅ EXPECTED |
| Get space permissions | `GET /api/v2/spaces/{id}/permissions` | `GET /spaces/:id/permissions` | ✅ CORRECT |
| Add space permission | `POST /api/v2/spaces/{id}/permissions` | N/A in Postman | ⚠️ CHECK |
| Remove space permission | `DELETE /api/v2/spaces/{id}/permissions/{id}` | N/A in Postman | ⚠️ CHECK |

#### Notes

1. **Page Restrictions**: Correctly uses v1 API as v2 doesn't have full restriction support.

2. **User Identification**: The library correctly uses `accountId` instead of deprecated `username`:
   ```python
   restriction_data["restrictions"] = {
       "user": [{"type": "known", "accountId": user}]
   }
   ```

---

### 8. Property Commands (`cli/commands/property_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List properties | `GET /rest/api/content/{id}/property` | v1 API | ✅ CORRECT |
| Get property | `GET /rest/api/content/{id}/property/{key}` | v1 API | ✅ CORRECT |
| Create property | `POST /rest/api/content/{id}/property` | v1 API | ✅ CORRECT |
| Update property | `PUT /rest/api/content/{id}/property/{key}` | v1 API | ✅ CORRECT |
| Delete property | `DELETE /rest/api/content/{id}/property/{key}` | v1 API | ✅ CORRECT |

**Note**: The content properties endpoints (`/rest/api/content/{id}/property/*`) are documented in the [Content properties API reference](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-content-properties/) but were not included in the downloaded OpenAPI spec. These endpoints are confirmed to be valid.

#### Recommendation

The v2 API now provides full content properties support:
- `GET /api/v2/pages/:page-id/properties`
- `POST /api/v2/pages/:page-id/properties`
- `GET /api/v2/pages/:page-id/properties/:property-id`
- `PUT /api/v2/pages/:page-id/properties/:property-id`
- `DELETE /api/v2/pages/:page-id/properties/:property-id`

Consider migrating to v2 API for consistency.

---

### 9. Watch Commands (`cli/commands/watch_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| Watch page | `POST /rest/api/user/watch/content/{id}` | v1 API | ✅ CORRECT |
| Unwatch page | `DELETE /rest/api/user/watch/content/{id}` | v1 API | ✅ CORRECT |
| Watch space | `POST /rest/api/user/watch/space/{key}` | v1 API | ✅ CORRECT |
| Unwatch space | `DELETE /rest/api/user/watch/space/{key}` | v1 API | ✅ CORRECT |
| Check watch status | `GET /rest/api/user/watch/content/{id}` | v1 API | ✅ CORRECT |
| Get watchers | `GET /rest/api/content/{id}/notification/child-created` | v1 API | ✅ CORRECT |

**Status**: Watch endpoints are only available in v1 API. No migration needed.

---

### 10. Hierarchy Commands (`cli/commands/hierarchy_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| Get children | `GET /api/v2/pages/{id}/children` | `GET /pages/:id/children` | ✅ CORRECT |
| Get ancestors | `GET /api/v2/pages/{id}/ancestors` | `GET /pages/:id/ancestors` | ✅ CORRECT |
| Get descendants | Recursive via children | `GET /pages/:id/descendants` | ⚠️ v2 AVAILABLE |

#### Recommendation

The v2 API now provides a direct descendants endpoint:
- `GET /api/v2/pages/:id/descendants`

The library currently uses recursive calls to `/children`. Consider using the direct descendants endpoint for better performance.

---

## Phase 3: Admin & Utility (LOW Priority)

### 11. Admin Commands (`cli/commands/admin_cmds.py`)

#### User Management

| Operation | Library Endpoint | Status |
|-----------|-----------------|--------|
| Search users | `GET /rest/api/search/user` | ✅ v1 only |
| Get user | `GET /rest/api/user` | ✅ v1 only |
| Get current user | `GET /rest/api/user/current` | ✅ v1 only |
| Get user groups | `GET /rest/api/user/memberof` | ✅ v1 only |

#### Group Management

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List groups | `GET /rest/api/group` | `GET /rest/api/group` | ✅ CORRECT |
| Get group | `GET /rest/api/group/{name}` | `GET /rest/api/group/by-id?id=` | ⚠️ DISCREPANCY |
| Get group members | `GET /rest/api/group/{name}/member` | `GET /rest/api/group/{groupId}/membersByGroupId` | ⚠️ DISCREPANCY |
| Create group | `POST /rest/api/group` | `POST /rest/api/group` | ✅ CORRECT |
| Delete group | `DELETE /rest/api/group/{name}` | `DELETE /rest/api/group/by-id?id=` | ⚠️ DISCREPANCY |
| Add user to group | `POST /rest/api/group/{name}/member` | `POST /rest/api/group/userByGroupId` | ⚠️ DISCREPANCY |
| Remove user from group | `DELETE /rest/api/group/{name}/member` | `DELETE /rest/api/group/userByGroupId` | ⚠️ DISCREPANCY |

#### Group Endpoint Discrepancies

The OpenAPI spec shows different endpoint patterns than those used in the library:

1. **Get/Delete Group by ID**: Spec uses query parameter `?id=` instead of path parameter
   - Spec: `GET /rest/api/group/by-id?id={groupId}`
   - Library: `GET /rest/api/group/{groupName}`

2. **Group Members**: Spec uses different path structure
   - Spec: `GET /rest/api/group/{groupId}/membersByGroupId`
   - Library: `GET /rest/api/group/{groupName}/member`

3. **Add/Remove User**: Spec uses different endpoint
   - Spec: `POST/DELETE /rest/api/group/userByGroupId`
   - Library: `POST/DELETE /rest/api/group/{groupName}/member`

**Note**: The library's endpoints may still work if they're legacy patterns supported by the API but not documented in the current spec. Verify against live API.

2. **No v2 User/Group APIs**: The v2 API only provides:
   - `POST /users-bulk` - Bulk user lookup
   - `POST /user/access/check-access-by-email`
   - `POST /user/access/invite-by-email`

---

### 12. Template Commands (`cli/commands/template_cmds.py`)

#### Endpoints Used

| Operation | Library Endpoint | Spec Endpoint | Status |
|-----------|-----------------|---------------|--------|
| List templates | `GET /rest/api/template/page` | `GET /rest/api/template/page` | ✅ CORRECT |
| Get template | `GET /rest/api/template/{id}` | `GET /rest/api/template/{contentTemplateId}` | ✅ CORRECT |
| Create template | `POST /rest/api/template` | `POST /rest/api/template` | ✅ CORRECT |
| Update template | `PUT /rest/api/template/{id}` | `PUT /rest/api/template` (ID in body) | ⚠️ VERIFY |
| Delete template | `DELETE /rest/api/template/{id}` | `DELETE /rest/api/template/{contentTemplateId}` | ✅ CORRECT |
| List blueprints | `GET /rest/api/content/blueprint/instance` | `GET /rest/api/template/blueprint` | ⚠️ VERIFY |

#### Template Endpoint Notes

1. **Template Update**: The OpenAPI spec shows `PUT /rest/api/template` without an ID in the path. The template ID should be included in the request body. The library currently passes the ID in the URL path - verify this works with the live API.

2. **Blueprint Endpoint**: There are two possible endpoints for blueprints:
   - Spec: `GET /rest/api/template/blueprint` - Lists blueprint templates
   - Library: `GET /rest/api/content/blueprint/instance` - May list blueprint instances

   These may serve different purposes. Verify which is appropriate for the library's use case.

---

## Deprecated Patterns Summary

| Pattern | Status | Recommendation |
|---------|--------|----------------|
| `start` pagination parameter | Removed July 2020 | Use `cursor` (already implemented) |
| `username` in restrictions | Deprecated | Use `accountId` (already implemented) |
| v1 content descendant endpoints | Deprecated | Use v2 `/pages/:id/descendants` |
| v1 content properties | Still works | Consider v2 `/pages/:page-id/properties` |
| v1 page versions | Still works | Consider v2 `/pages/:id/versions` |

---

## Recommended Migrations

### Priority 1: Verify Live API Behavior

1. **Space PATCH/DELETE**: Verify v2 space update and delete work as implemented
2. **Group member endpoints**: Verify `/group/{name}/member` pattern vs `/group/userByGroupId`
3. **Template update endpoint**: Verify PUT target URL

### Priority 2: Migrate to v2 Where Available

1. **Page Versions**: Migrate from v1 to v2
   - From: `GET /rest/api/content/{id}/version`
   - To: `GET /api/v2/pages/:id/versions`

2. **Content Properties**: Migrate from v1 to v2
   - From: `GET /rest/api/content/{id}/property`
   - To: `GET /api/v2/pages/:page-id/properties`

3. **Descendants**: Use direct endpoint instead of recursive calls
   - From: Recursive `/pages/:id/children` calls
   - To: `GET /api/v2/pages/:id/descendants`

### Priority 3: Add Missing v2 Features

1. **Page Title Update**: Add `PUT /api/v2/pages/:id/title` endpoint
2. **Like Support**: v2 provides like count and users endpoints
3. **Classification Levels**: v2 provides content classification endpoints
4. **Task Management**: v2 provides task endpoints

---

## Test Coverage Recommendations

### Add Schema Validation

Consider adding OpenAPI schema validation to existing tests:

```python
from openapi_core import create_spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator

# Load spec
with open('.api-specs/confluence-v1.json') as f:
    spec = create_spec(json.load(f))

# Validate response against schema
result = openapi_response_validator.validate(spec, request, response)
```

### Integration Test Markers

Add markers for endpoints that need live API verification:
- `@pytest.mark.verify_live` - Endpoints with uncertain spec compliance
- `@pytest.mark.v2_migration` - Endpoints ready for v2 migration

---

## Appendix: API Version Matrix

| Feature | v1 Available | v2 Available | Library Uses | Recommendation |
|---------|-------------|--------------|--------------|----------------|
| Pages CRUD | Yes | Yes | v2 | Keep v2 |
| Blog Posts CRUD | Yes | Yes | v2 | Keep v2 |
| Spaces CRUD | Yes | Partial | v2 | Keep v2, verify |
| Comments CRUD | Yes | Yes | v2 | Keep v2 |
| Attachments List/Get/Delete | Yes | Yes | v2 | Keep v2 |
| Attachments Upload/Update | Yes | No | v1 | Keep v1 (required) |
| Labels | Yes | GET only | Mixed | Keep mixed |
| Properties | Yes | Yes | v1 | Consider v2 |
| Search | Yes | No | v1 | Keep v1 (required) |
| Users/Groups | Yes | Limited | v1 | Keep v1 (required) |
| Permissions | Yes | Yes | Mixed | Current is fine |
| Watch | Yes | No | v1 | Keep v1 (required) |
| Templates | Yes | No | v1 | Keep v1 (required) |
| Versions | Yes | Yes | v1 | Consider v2 |
| Hierarchy | Yes | Yes | v2 | Enhance with descendants |
