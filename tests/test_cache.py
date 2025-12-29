"""Tests for cache module."""

import pytest
import tempfile
import time
from pathlib import Path
from confluence_assistant_skills_lib import Cache, cached, get_cache


class TestCache:
    """Tests for Cache class."""

    @pytest.fixture
    def cache(self):
        """Create a cache instance with a temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Cache(cache_dir=Path(tmpdir), default_ttl=60)

    def test_set_and_get(self, cache):
        cache.set("key1", {"value": "test"})
        result = cache.get("key1")
        assert result == {"value": "test"}

    def test_get_missing_key(self, cache):
        assert cache.get("nonexistent") is None
        assert cache.get("nonexistent", default="default") == "default"

    def test_ttl_expiration(self, cache):
        cache.set("key1", "value", ttl=1)
        assert cache.get("key1") == "value"

        time.sleep(1.1)
        assert cache.get("key1") is None

    def test_delete(self, cache):
        cache.set("key1", "value")
        assert cache.delete("key1") is True
        assert cache.get("key1") is None

    def test_delete_nonexistent(self, cache):
        assert cache.delete("nonexistent") is False

    def test_clear(self, cache):
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        count = cache.clear()
        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_disabled_cache(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=Path(tmpdir), enabled=False)

            cache.set("key1", "value")
            assert cache.get("key1") is None

    def test_stats(self, cache):
        cache.set("key1", "value1")
        cache.set("key2", "value2")

        stats = cache.stats()
        assert stats["enabled"] is True
        assert stats["entries"] == 2

    def test_cleanup_expired(self, cache):
        cache.set("key1", "value1", ttl=1)
        cache.set("key2", "value2", ttl=60)

        time.sleep(1.1)
        count = cache.cleanup_expired()

        assert count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"


class TestCachedDecorator:
    """Tests for cached decorator."""

    def test_caches_result(self):
        call_count = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            test_cache = Cache(cache_dir=Path(tmpdir))

            @cached(ttl=60, cache=test_cache)
            def expensive_function(x):
                nonlocal call_count
                call_count += 1
                return x * 2

            result1 = expensive_function(5)
            result2 = expensive_function(5)

            assert result1 == 10
            assert result2 == 10
            assert call_count == 1

    def test_different_args_not_cached(self):
        call_count = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            test_cache = Cache(cache_dir=Path(tmpdir))

            @cached(ttl=60, cache=test_cache)
            def add(a, b):
                nonlocal call_count
                call_count += 1
                return a + b

            result1 = add(1, 2)
            result2 = add(2, 3)

            assert result1 == 3
            assert result2 == 5
            assert call_count == 2

    def test_key_prefix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_cache = Cache(cache_dir=Path(tmpdir))

            @cached(ttl=60, key_prefix="test", cache=test_cache)
            def func():
                return "result"

            result = func()
            assert result == "result"
