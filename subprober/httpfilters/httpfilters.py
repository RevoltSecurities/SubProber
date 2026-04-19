import re
import asyncio
from typing import Optional, List,Any, Protocol
from abc import ABC, abstractmethod
from urllib.parse import urlparse

class ResponseProtocol(Protocol):
    """Protocol for HTTP response objects"""
    @property
    def status_code(self) -> int: ...

    @property
    def text(self) -> str: ...

    @property
    def url(self) -> Any: ...

    @property
    def elapsed(self) -> Any: ...


class ResponseAdapter(ABC):
    """Abstract base class for response adapters"""
    def __init__(self, response: Any):
        self._response = response

    @abstractmethod
    def get_status_code(self) -> int:
        """Get HTTP status code"""
        pass

    @abstractmethod
    def get_text(self) -> str:
        """Get response body as text"""
        pass

    @abstractmethod
    def get_url(self) -> str:
        """Get request URL"""
        pass

    @abstractmethod
    def get_url_path(self) -> str:
        """Get URL path component"""
        pass

    @abstractmethod
    def get_response_time(self) -> float:
        """Get response time in seconds"""
        pass

    @abstractmethod
    def get_headers(self) -> dict:
        """Get response headers"""
        pass


class RequestsAdapter(ResponseAdapter):
    """Adapter for requests.Response"""
    def get_status_code(self) -> int:
        return self._response.status_code

    def get_text(self) -> str:
        return self._response.text

    def get_url(self) -> str:
        return str(self._response.url)

    def get_url_path(self) -> str:
        return urlparse(str(self._response.url)).path

    def get_response_time(self) -> float:
        return self._response.elapsed.total_seconds()

    def get_headers(self) -> dict:
        return dict(self._response.headers)


class AiohttpAdapter(ResponseAdapter):
    """Adapter for aiohttp.ClientResponse"""
    def __init__(self, response: Any, text: str = "", response_time: float = 0.0):
        super().__init__(response)
        self._text = text
        self._response_time = response_time

    def get_status_code(self) -> int:
        return self._response.status

    def get_text(self) -> str:
        return self._text

    def get_url(self) -> str:
        return str(self._response.url)

    def get_url_path(self) -> str:
        return self._response.url.path

    def get_response_time(self) -> float:
        return self._response_time

    def get_headers(self) -> dict:
        return dict(self._response.headers)


class HttpxAdapter(ResponseAdapter):
    """Adapter for httpx.Response"""
    def get_status_code(self) -> int:
        return self._response.status_code

    def get_text(self) -> str:
        return self._response.text

    def get_url(self) -> str:
        return str(self._response.url)

    def get_url_path(self) -> str:
        return self._response.url.path

    def get_response_time(self) -> float:
        return self._response.elapsed.total_seconds()

    def get_headers(self) -> dict:
        return dict(self._response.headers)


class CustomAdapter(ResponseAdapter):
    """Adapter for custom response objects with dict-like interface"""
    def get_status_code(self) -> int:
        return self._response.get('status_code', 0)

    def get_text(self) -> str:
        return self._response.get('text', '')

    def get_url(self) -> str:
        return self._response.get('url', '')

    def get_url_path(self) -> str:
        url = self._response.get('url', '')
        return urlparse(url).path if url else ''

    def get_response_time(self) -> float:
        return self._response.get('response_time', 0.0)

    def get_headers(self) -> dict:
        return self._response.get('headers', {})



class HttpMatcher:
    """
    Universal HTTP response matcher supporting multiple libraries.
    Returns True to INCLUDE responses that match criteria.

    Supports:
    - requests library
    - aiohttp library
    - httpx library
    - Custom response objects (dict-like)
    """

    def __init__(self):
        self._adapters = {
            'requests': RequestsAdapter,
            'aiohttp': AiohttpAdapter,
            'httpx': HttpxAdapter,
            'custom': CustomAdapter,
        }

    def _detect_response_type(self, response: Any) -> str:
        """Auto-detect response type"""
        response_type = type(response).__module__

        if 'requests' in response_type:
            return 'requests'
        elif 'aiohttp' in response_type:
            return 'aiohttp'
        elif 'httpx' in response_type:
            return 'httpx'
        elif isinstance(response, dict):
            return 'custom'
        else:
            # Try to detect by attributes
            if hasattr(response, 'status_code') and hasattr(response, 'elapsed'):
                return 'requests'
            elif hasattr(response, 'status') and hasattr(response, 'url'):
                return 'aiohttp'
            else:
                return 'custom'

    def _get_adapter(self, response: Any, **kwargs) -> ResponseAdapter:
        """Get appropriate adapter for response type"""
        response_type = self._detect_response_type(response)
        adapter_class = self._adapters[response_type]

        if response_type == 'aiohttp':
            # Aiohttp needs extra parameters
            return adapter_class(
                response,
                text=kwargs.get('text', ''),
                response_time=kwargs.get('response_time', 0.0)
            )
        return adapter_class(response)



    async def match_by_code(self, response: Any, code_list: Optional[List[int]] = None, **kwargs) -> bool:
        """
        Match by status code - returns True if status code in list.
        If code_list is None or empty, returns True (no filtering).
        """
        if not code_list:
            return True

        adapter = self._get_adapter(response, **kwargs)
        status_code = adapter.get_status_code()
        return status_code in code_list

    async def match_code_range(self, response: Any, code: Optional[str] = None, **kwargs) -> bool:
        """
        Match by status code range (e.g., '200-299').
        Returns True if status code is within range.
        """
        if not code:
            return True

        try:
            min_code, max_code = map(int, code.split("-"))
            adapter = self._get_adapter(response, **kwargs)
            status_code = adapter.get_status_code()
            return min_code <= status_code <= max_code
        except (ValueError, AttributeError):
            return True

    async def match_url_path_contains(self, response: Any, paths: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Match if URL path contains any of the strings.
        Returns True if any path is found.
        """
        if not paths:
            return True

        adapter = self._get_adapter(response, **kwargs)
        url_path = adapter.get_url_path()
        return any(str(path) in url_path for path in paths)

    async def match_word_body(self, response: Any, words: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Match if response body contains any of the words.
        Returns True if any word is found.
        """
        if not words:
            return True

        adapter = self._get_adapter(response, **kwargs)
        text = adapter.get_text()
        return any(str(word) in text for word in words)

    async def match_by_regex(self, response: Any, regexes: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Match if response body matches any regex pattern.
        Returns True if any pattern matches.
        """
        if not regexes:
            return True

        adapter = self._get_adapter(response, **kwargs)
        text = adapter.get_text()
        return any(re.search(pattern, text) for pattern in regexes)

    async def match_response_time(self, response: Any, max_time: Optional[float] = None, **kwargs) -> bool:
        """
        Match if response time is under threshold.
        Returns True if response time <= max_time.
        """
        if max_time is None:
            return True

        adapter = self._get_adapter(response, **kwargs)
        response_time = adapter.get_response_time()
        return response_time <= max_time

    async def match_by_ints(self, value: int, int_list: Optional[List[int]] = None) -> bool:
        """
        Match integer value against list.
        Used for content length, line count, word count.
        Returns True if value in list.
        """
        if not int_list:
            return True
        return value in int_list

    async def match(
            self,
            response: Any,
            status_codes: Optional[List[int]] = None,
            status_code_range: Optional[str] = None,
            url_path_contains: Optional[List[str]] = None,
            words: Optional[List[str]] = None,
            regex_patterns: Optional[List[str]] = None,
            max_response_time: Optional[float] = None,
            headers_contain: Optional[dict] = None,
            **kwargs
    ) -> bool:
        """
        Match response against multiple criteria (ALL conditions must pass).
        Returns True if ALL conditions match, False otherwise.
        """
        if status_codes and not await self.match_by_code(response, status_codes, **kwargs):
            return False

        if status_code_range and not await self.match_code_range(response, status_code_range, **kwargs):
            return False

        if url_path_contains and not await self.match_url_path_contains(response, url_path_contains, **kwargs):
            return False

        if words and not await self.match_word_body(response, words, **kwargs):
            return False

        if regex_patterns and not await self.match_by_regex(response, regex_patterns, **kwargs):
            return False

        if max_response_time is not None and not await self.match_response_time(response, max_response_time, **kwargs):
            return False

        if headers_contain:
            adapter = self._get_adapter(response, **kwargs)
            response_headers = adapter.get_headers()
            for key, value in headers_contain.items():
                if key not in response_headers:
                    return False
                if value and response_headers[key] != value:
                    return False

        return True

    async def match_any(
            self,
            response: Any,
            status_codes: Optional[List[int]] = None,
            status_code_range: Optional[str] = None,
            url_path_contains: Optional[List[str]] = None,
            words: Optional[List[str]] = None,
            regex_patterns: Optional[List[str]] = None,
            max_response_time: Optional[float] = None,
            headers_contain: Optional[dict] = None,
            **kwargs
    ) -> bool:
        """
        Match response against multiple criteria (ANY condition can pass).
        Returns True if ANY condition matches, False if all fail.
        """
        conditions = []

        if status_codes:
            conditions.append(self.match_by_code(response, status_codes, **kwargs))

        if status_code_range:
            conditions.append(self.match_code_range(response, status_code_range, **kwargs))

        if url_path_contains:
            conditions.append(self.match_url_path_contains(response, url_path_contains, **kwargs))

        if words:
            conditions.append(self.match_word_body(response, words, **kwargs))

        if regex_patterns:
            conditions.append(self.match_by_regex(response, regex_patterns, **kwargs))

        if max_response_time is not None:
            conditions.append(self.match_response_time(response, max_response_time, **kwargs))

        if not conditions:
            return True

        results = await asyncio.gather(*conditions)
        return any(results)


class HttpFilter:
    """
    Universal HTTP response filter supporting multiple libraries.
    Returns False to EXCLUDE responses that match criteria.
    Returns True to KEEP responses that don't match.

    Filters are the INVERSE of matchers.
    """

    def __init__(self):
        self._matcher = HttpMatcher()

    async def filter_by_code(self, response: Any, code_list: Optional[List[int]] = None, **kwargs) -> bool:
        """
        Filter by status code - exclude if matches.
        Returns False if status code in exclude list (EXCLUDE).
        Returns True if status code not in list (KEEP).
        """
        if not code_list:
            return True

        adapter = self._matcher._get_adapter(response, **kwargs)
        status_code = adapter.get_status_code()
        # Inverse: return False to EXCLUDE
        return status_code not in code_list

    async def filter_code_range(self, response: Any, code: Optional[str] = None, **kwargs) -> bool:
        """
        Filter by status code range - exclude if in range.
        Returns False if status code in range (EXCLUDE).
        Returns True if status code not in range (KEEP).
        """
        if not code:
            return True

        try:
            min_code, max_code = map(int, code.split("-"))
            adapter = self._matcher._get_adapter(response, **kwargs)
            status_code = adapter.get_status_code()
            # Inverse: return False to EXCLUDE
            return not (min_code <= status_code <= max_code)
        except (ValueError, AttributeError):
            return True

    async def filter_url_path_contains(self, response: Any, paths: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Filter by URL path - exclude if contains.
        Returns False if any path found (EXCLUDE).
        Returns True if no path found (KEEP).
        """
        if not paths:
            return True

        adapter = self._matcher._get_adapter(response, **kwargs)
        url_path = adapter.get_url_path()
        # Inverse: return False to EXCLUDE
        for path in paths:
            if str(path) in url_path:
                return False
        return True

    async def filter_word_body(self, response: Any, words: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Filter by words in body - exclude if contains.
        Returns False if any word found (EXCLUDE).
        Returns True if no word found (KEEP).
        """
        if not words:
            return True

        adapter = self._matcher._get_adapter(response, **kwargs)
        text = adapter.get_text()
        # Inverse: return False to EXCLUDE
        for word in words:
            if str(word) in text:
                return False
        return True

    async def filter_by_regex(self, response: Any, regexes: Optional[List[str]] = None, **kwargs) -> bool:
        """
        Filter by regex - exclude if matches.
        Returns False if any regex matches (EXCLUDE).
        Returns True if no regex matches (KEEP).
        """
        if not regexes:
            return True

        adapter = self._matcher._get_adapter(response, **kwargs)
        text = adapter.get_text()
        # Inverse: return False to EXCLUDE
        for regex in regexes:
            if re.search(regex, text):
                return False
        return True

    async def filter_response_time(self, response: Any, max_time: Optional[float] = None, **kwargs) -> bool:
        """
        Filter by response time - exclude if exceeds threshold.
        Returns False if response time > max_time (EXCLUDE).
        Returns True if response time <= max_time (KEEP).
        """
        if max_time is None:
            return True

        adapter = self._matcher._get_adapter(response, **kwargs)
        response_time = adapter.get_response_time()
        # Inverse: return False to EXCLUDE
        return response_time <= max_time

    async def filter_by_ints(self, value: int, int_list: Optional[List[int]] = None) -> bool:
        """
        Filter by integer value - exclude if matches.
        Used for content length, line count, word count.
        Returns False if value in exclude list (EXCLUDE).
        Returns True if value not in list (KEEP).
        """
        if not int_list:
            return True
        return value not in int_list

    async def filter(
            self,
            response: Any,
            status_codes: Optional[List[int]] = None,
            status_code_range: Optional[str] = None,
            url_path_contains: Optional[List[str]] = None,
            words: Optional[List[str]] = None,
            regex_patterns: Optional[List[str]] = None,
            max_response_time: Optional[float] = None,
            headers_contain: Optional[dict] = None,
            **kwargs
    ) -> bool:
        """
        Filter response against multiple criteria (ANY match excludes).
        Returns False to EXCLUDE if ANY condition matches.
        Returns True to KEEP if NO conditions match.
        """
        # If ANY condition matches, EXCLUDE the response
        if status_codes and not await self.filter_by_code(response, status_codes, **kwargs):
            return False

        if status_code_range and not await self.filter_code_range(response, status_code_range, **kwargs):
            return False

        if url_path_contains and not await self.filter_url_path_contains(response, url_path_contains, **kwargs):
            return False

        if words and not await self.filter_word_body(response, words, **kwargs):
            return False

        if regex_patterns and not await self.filter_by_regex(response, regex_patterns, **kwargs):
            return False

        if max_response_time is not None and not await self.filter_response_time(response, max_response_time, **kwargs):
            return False

        if headers_contain:
            adapter = self._matcher._get_adapter(response, **kwargs)
            response_headers = adapter.get_headers()
            for key, value in headers_contain.items():
                if key in response_headers:
                    if not value or response_headers[key] == value:
                        return False  # Header matched, EXCLUDE

        return True  # No conditions matched, KEEP

    async def filter_all(
            self,
            response: Any,
            status_codes: Optional[List[int]] = None,
            status_code_range: Optional[str] = None,
            url_path_contains: Optional[List[str]] = None,
            words: Optional[List[str]] = None,
            regex_patterns: Optional[List[str]] = None,
            max_response_time: Optional[float] = None,
            headers_contain: Optional[dict] = None,
            **kwargs
    ) -> bool:
        """
        Filter with ALL conditions - only exclude if ALL criteria match.
        Returns False to EXCLUDE if ALL conditions match.
        Returns True to KEEP if ANY condition doesn't match.
        """
        # If ALL conditions match, EXCLUDE the response
        all_matched = await self._matcher.match(
            response,
            status_codes=status_codes,
            status_code_range=status_code_range,
            url_path_contains=url_path_contains,
            words=words,
            regex_patterns=regex_patterns,
            max_response_time=max_response_time,
            headers_contain=headers_contain,
            **kwargs
        )

        return not all_matched



if __name__ == "__main__":
    async def test_matcher_filter():
        """Test examples for matcher and filter"""

        # Create test response (dict-like)
        test_response = {
            'status_code': 200,
            'text': 'Welcome to the admin dashboard',
            'url': 'https://example.com/admin/dashboard',
            'response_time': 0.5,
            'headers': {'Content-Type': 'text/html'}
        }

        matcher = HttpMatcher()
        filter_obj = HttpFilter()

        print("=" * 70)
        print("MATCHER TESTS (Returns True to INCLUDE)")
        print("=" * 70)

        # Test 1: Match by status code
        result = await matcher.match_by_code(test_response, [200, 201])
        print(f"✓ Match status 200: {result}")  # True

        # Test 2: Match by word
        result = await matcher.match_word_body(test_response, ['admin', 'dashboard'])
        print(f"✓ Match words: {result}")  # True

        # Test 3: Match by code range
        result = await matcher.match_code_range(test_response, '200-299')
        print(f"✓ Match code range 200-299: {result}")  # True

        # Test 4: Match response time
        result = await matcher.match_response_time(test_response, 1.0)
        print(f"✓ Match response time < 1.0s: {result}")  # True

        print("\n" + "=" * 70)
        print("FILTER TESTS (Returns False to EXCLUDE)")
        print("=" * 70)

        # Test 5: Filter by status code (should keep 200)
        result = await filter_obj.filter_by_code(test_response, [404, 500])
        print(f"✓ Filter 404/500 (keep 200): {result}")  # True (keep)

        # Test 6: Filter by status code (should exclude 200)
        result = await filter_obj.filter_by_code(test_response, [200])
        print(f"✓ Filter 200 (exclude 200): {result}")  # False (exclude)

        # Test 7: Filter by word (should exclude if contains 'admin')
        result = await filter_obj.filter_word_body(test_response, ['admin'])
        print(f"✓ Filter 'admin' word: {result}")  # False (exclude)

        # Test 8: Filter by code range (should keep 200)
        result = await filter_obj.filter_code_range(test_response, '400-599')
        print(f"✓ Filter 4xx/5xx range (keep 200): {result}")  # True (keep)

        print("\n" + "=" * 70)
        print("COMBINED TESTS")
        print("=" * 70)

        # Test 9: Combined matcher (all must pass)
        result = await matcher.match(
            test_response,
            status_codes=[200],
            words=['admin'],
            max_response_time=1.0
        )
        print(f"✓ Combined match (all pass): {result}")  # True

        # Test 10: Combined filter (any match excludes)
        result = await filter_obj.filter(
            test_response,
            status_codes=[404, 500],  # Won't match
            words=['error']  # Won't match
        )
        print(f"✓ Combined filter (keep): {result}")  # True (keep)

        result = await filter_obj.filter(
            test_response,
            status_codes=[200],  # Will match - exclude!
        )
        print(f"✓ Combined filter (exclude): {result}")  # False (exclude)

    # Run tests
    asyncio.run(test_matcher_filter())