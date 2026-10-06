import time
import logging
import requests
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from typing import Optional

from config import (
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    REQUEST_DELAY,
    USER_AGENT
)

logger = logging.getLogger("scraper_pipeline")


class HTTPClient:
    """Wrapper around requests.Session providing retries, timeouts, rate limiting, and exception safety."""

    def __init__(
        self,
        timeout: int = REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRIES,
        backoff_factor: float = BACKOFF_FACTOR,
        delay: float = REQUEST_DELAY,
        user_agent: str = USER_AGENT
    ):
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

        # Retry strategy for transient HTTP errors
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def get(self, url: str) -> Optional[requests.Response]:
        """Performs HTTP GET request with error handling and rate-limiting delay."""
        if self.delay > 0:
            time.sleep(self.delay)

        try:
            logger.debug(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred while fetching URL: {url}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error {e.response.status_code} for URL: {url}")
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection failure connecting to URL: {url}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for URL {url}: {e}")
        return None

    def close(self):
        """Closes the underlying HTTP session."""
        self.session.close()
