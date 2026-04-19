from typing import Dict, Any, Optional
from urllib.parse import urlparse


class URLBuilder:
    """Intelligent URL builder that handles all input types"""

    @staticmethod
    def parse_url(url: str) -> Optional[Dict[str, Any]]:
        """
        Parse URL into components, handling all formats:
        - google.com
        - https://google.com
        - http://google.com:8080
        - 192.168.1.1:8080
        - [::1]:8080
        - https://[::1]:8080/path
        """
        try:
            parsed = urlparse(url)

            scheme = parsed.scheme if parsed.scheme else 'https'

            netloc = parsed.netloc
            host = None
            port = None

            if netloc:
                if netloc.startswith('['):
                    if ']:' in netloc:
                        bracket_end = netloc.index(']')
                        host = netloc[1:bracket_end]
                        port_str = netloc[bracket_end + 2:]
                        if port_str.isdigit():
                            port = int(port_str)
                    elif netloc.endswith(']'):
                        host = netloc[1:-1]
                    else:
                        host = netloc
                else:
                    if ':' in netloc:
                        colon_count = netloc.count(':')
                        if colon_count == 1:
                            parts = netloc.rsplit(':', 1)
                            if parts[1].isdigit():
                                host = parts[0]
                                port = int(parts[1])
                            else:
                                host = netloc
                        else:
                            host = netloc
                    else:
                        host = netloc

            path = parsed.path if parsed.path and parsed.path != '/' else None

            return {
                'scheme': scheme,
                'host': host,
                'port': port,
                'path': path
            }
        except Exception:
            return None

    @staticmethod
    def build(scheme: str, host: str, port: Optional[int] = None, path: Optional[str] = None) -> str:
        """
        Build URL intelligently from components.

        Rules:
        - If port is 80 and scheme is https, change scheme to http
        - Only add port if provided AND not default (80 for http, 443 for https)
        - Only add path if provided
        - Handle IPv6 addresses with brackets
        """
        if port == 80 and scheme == 'https':
            scheme = 'http'

        if host and ':' in host and not host.startswith('['):
            if host.count(':') > 1:
                host = f'[{host}]'

        url = f"{scheme}://{host}"

        if port is not None:
            if not ((port == 80 and scheme == 'http') or (port == 443 and scheme == 'https')):
                url += f":{port}"

        if path:
            if not path.startswith('/'):
                path = '/' + path
            url += path

        return url

    @staticmethod
    def normalize_input(raw_input: str) -> str:
        """
        Normalize raw input for consistent parsing.
        - Strips whitespace
        - Adds https:// if no scheme present
        """
        raw_input = raw_input.strip()

        if not raw_input.startswith(('http://', 'https://')):
            if raw_input.count(':') > 1 and not raw_input.startswith('['):
                if ']:' in raw_input:
                    raw_input = f'https://{raw_input}'
                else:
                    raw_input = f'https://[{raw_input}]'
            else:
                raw_input = f'https://{raw_input}'

        return raw_input


# Example usage and testing
if __name__ == "__main__":
    builder = URLBuilder()

    test_cases = [
        # Domains
        "google.com",
        "google.com:8080",
        "google.com:80",
        "https://google.com",
        "http://google.com",
        "https://google.com:8080",
        "https://google.com/path",
        "https://google.com:8080/path",

        # IPv4
        "192.168.1.1",
        "192.168.1.1:8080",
        "192.168.1.1:80",
        "https://192.168.1.1",
        "http://192.168.1.1:8080",
        "https://192.168.1.1/api/v1",

        # IPv6
        "::1",
        "[::1]",
        "[::1]:8080",
        "https://[::1]",
        "https://[::1]:8080",
        "https://[::1]/path",
        "2001:db8::1",
        "[2001:db8::1]:8080",
    ]

    print("Testing URLBuilder:\n")
    for test in test_cases:
        normalized = builder.normalize_input(test)
        parsed = builder.parse_url(normalized)
        if parsed:
            rebuilt = builder.build(
                parsed['scheme'],
                parsed['host'],
                parsed['port'],
                parsed['path']
            )
            print(f"Input:    {test}")
            print(f"Parsed:   {parsed}")
            print(f"Rebuilt:  {rebuilt}")
            print()