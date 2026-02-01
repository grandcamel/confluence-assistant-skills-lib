"""
Live Integration Tests for Confluence-AS Library.

This package contains live integration tests that require a real Confluence
instance (Cloud or Server). Tests are skipped by default unless the --live
flag is provided.

Usage:
    # Run all live tests
    pytest tests/live/ --live -v

    # Run with existing space (faster)
    pytest tests/live/ --live --space-key MYSPACE -v

    # Keep space for debugging
    pytest tests/live/ --live --keep-space -v

Environment Variables:
    CONFLUENCE_API_TOKEN: API token for authentication
    CONFLUENCE_EMAIL: Email associated with Atlassian account
    CONFLUENCE_SITE_URL: Confluence Cloud URL (e.g., https://company.atlassian.net)

For Docker-based testing (optional):
    CONFLUENCE_TEST_URL: External Confluence URL (skips Docker)
    CONFLUENCE_TEST_EMAIL: Email for external Confluence
    CONFLUENCE_TEST_TOKEN: API token for external Confluence
    CONFLUENCE_TEST_LICENSE: Confluence license key (required for Docker)
"""
