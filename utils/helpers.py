import hashlib
from urllib.parse import urljoin, urlparse
from typing import Sequence


def make_absolute_url(base_url: str, relative_url: str) -> str:
    """Resolves a relative URL against a base URL to form a complete absolute URL."""
    if not relative_url:
        return ""
    return urljoin(base_url, relative_url)


def is_valid_url(url: str) -> bool:
    """Checks if a string is a valid absolute HTTP/HTTPS URL."""
    if not url or not isinstance(url, str):
        return False
    parsed = urlparse(url)
    return bool(parsed.scheme in ("http", "https") and parsed.netloc)


def compute_composite_hash(key_parts: Sequence[str]) -> str:
    """Generates an MD5 hash hex digest from a sequence of normalized key strings."""
    composite_string = "||".join(str(part).strip() for part in key_parts)
    return hashlib.md5(composite_string.encode("utf-8")).hexdigest()
