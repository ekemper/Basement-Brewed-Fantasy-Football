import time
import random
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any
import logging
from collections import defaultdict, deque
import requests
from functools import wraps

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Advanced rate limiter with exponential backoff and retry logic.
    Supports per-domain rate limiting and adaptive delays.
    """
    
    def __init__(self, 
                 default_delay: float = 1.0,
                 max_retries: int = 3,
                 backoff_factor: float = 2.0,
                 jitter: bool = True):
        """
        Initialize the rate limiter.
        
        Args:
            default_delay (float): Default delay between requests in seconds
            max_retries (int): Maximum number of retry attempts
            backoff_factor (float): Exponential backoff multiplier
            jitter (bool): Add random jitter to delays
        """
        self.default_delay = default_delay
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.logger = logger
        
        # Per-domain rate limiting
        self.domain_delays = defaultdict(lambda: default_delay)
        self.last_request_times = defaultdict(float)
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        
        # Request history for adaptive rate limiting
        self.request_history = defaultdict(lambda: deque(maxlen=100))
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retries': 0,
            'rate_limit_hits': 0,
            'total_delay_time': 0.0
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for per-domain rate limiting."""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except Exception:
            return 'default'
    
    def _calculate_delay(self, domain: str, attempt: int = 0) -> float:
        """
        Calculate delay for a domain based on history and attempt number.
        
        Args:
            domain (str): Domain to calculate delay for
            attempt (int): Current attempt number (for exponential backoff)
            
        Returns:
            float: Delay in seconds
        """
        base_delay = self.domain_delays[domain]
        
        # Apply exponential backoff for retries
        if attempt > 0:
            base_delay *= (self.backoff_factor ** attempt)
        
        # Add jitter to prevent thundering herd
        if self.jitter:
            jitter_factor = random.uniform(0.8, 1.2)
            base_delay *= jitter_factor
        
        # Adaptive rate limiting based on error rate
        error_rate = self.error_counts[domain] / max(self.request_counts[domain], 1)
        if error_rate > 0.1:  # If error rate > 10%, increase delay
            base_delay *= (1 + error_rate)
        
        return base_delay
    
    def _should_retry(self, response: Optional[requests.Response], 
                     exception: Optional[Exception]) -> bool:
        """
        Determine if a request should be retried.
        
        Args:
            response: HTTP response object (if any)
            exception: Exception that occurred (if any)
            
        Returns:
            bool: True if should retry, False otherwise
        """
        if exception:
            # Retry on network errors
            if isinstance(exception, (requests.ConnectionError, 
                                    requests.Timeout, 
                                    requests.RequestException)):
                return True
        
        if response:
            # Retry on rate limiting and server errors
            if response.status_code in [429, 500, 502, 503, 504]:
                return True
            
            # Don't retry on client errors (except rate limiting)
            if 400 <= response.status_code < 500:
                return False
        
        return False
    
    def _update_domain_delay(self, domain: str, success: bool, 
                           response_time: float) -> None:
        """
        Update domain delay based on request success and response time.
        
        Args:
            domain (str): Domain to update
            success (bool): Whether the request was successful
            response_time (float): Response time in seconds
        """
        with self.lock:
            if success:
                # Gradually decrease delay for successful requests
                if response_time < 1.0:  # Fast response
                    self.domain_delays[domain] *= 0.95
                    self.domain_delays[domain] = max(
                        self.domain_delays[domain], 
                        self.default_delay * 0.5
                    )
            else:
                # Increase delay for failed requests
                self.domain_delays[domain] *= 1.5
                self.domain_delays[domain] = min(
                    self.domain_delays[domain], 
                    self.default_delay * 10
                )
    
    def wait_if_needed(self, url: str) -> float:
        """
        Wait if needed based on rate limiting rules.
        
        Args:
            url (str): URL being requested
            
        Returns:
            float: Time waited in seconds
        """
        domain = self._extract_domain(url)
        
        with self.lock:
            now = time.time()
            last_request = self.last_request_times[domain]
            required_delay = self._calculate_delay(domain)
            
            time_since_last = now - last_request
            if time_since_last < required_delay:
                wait_time = required_delay - time_since_last
                self.logger.debug(f"Rate limiting: waiting {wait_time:.2f}s for {domain}")
                
                # Release lock before sleeping
                self.lock.release()
                time.sleep(wait_time)
                self.lock.acquire()
                
                self.stats['total_delay_time'] += wait_time
                self.stats['rate_limit_hits'] += 1
                
                # Update last request time
                self.last_request_times[domain] = time.time()
                return wait_time
            else:
                self.last_request_times[domain] = now
                return 0.0
    
    def make_request(self, url: str, method: str = 'GET', 
                    session: Optional[requests.Session] = None,
                    **kwargs) -> requests.Response:
        """
        Make a rate-limited HTTP request with retry logic.
        
        Args:
            url (str): URL to request
            method (str): HTTP method
            session: Optional requests session
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: HTTP response
            
        Raises:
            requests.RequestException: If all retries fail
        """
        domain = self._extract_domain(url)
        session = session or requests
        
        for attempt in range(self.max_retries + 1):
            try:
                # Wait if needed (with exponential backoff for retries)
                wait_time = self.wait_if_needed(url)
                if attempt > 0:
                    additional_wait = self._calculate_delay(domain, attempt) - self._calculate_delay(domain, 0)
                    if additional_wait > 0:
                        self.logger.debug(f"Retry {attempt}: additional wait {additional_wait:.2f}s")
                        time.sleep(additional_wait)
                        self.stats['total_delay_time'] += additional_wait
                
                # Make the request
                start_time = time.time()
                
                if method.upper() == 'GET':
                    response = session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = session.post(url, **kwargs)
                else:
                    response = session.request(method, url, **kwargs)
                
                response_time = time.time() - start_time
                
                # Update statistics
                with self.lock:
                    self.stats['total_requests'] += 1
                    self.request_counts[domain] += 1
                    
                    if attempt > 0:
                        self.stats['retries'] += 1
                
                # Check if request was successful
                if response.status_code < 400:
                    # Success
                    with self.lock:
                        self.stats['successful_requests'] += 1
                    
                    self._update_domain_delay(domain, True, response_time)
                    self.logger.debug(f"Successful request to {domain} (attempt {attempt + 1})")
                    return response
                
                else:
                    # HTTP error
                    with self.lock:
                        self.stats['failed_requests'] += 1
                        self.error_counts[domain] += 1
                    
                    if not self._should_retry(response, None):
                        self.logger.warning(f"Non-retryable error {response.status_code} for {url}")
                        response.raise_for_status()
                    
                    if attempt < self.max_retries:
                        self.logger.warning(f"HTTP {response.status_code} for {url}, retrying (attempt {attempt + 1})")
                        self._update_domain_delay(domain, False, response_time)
                        continue
                    else:
                        self.logger.error(f"Max retries exceeded for {url}")
                        response.raise_for_status()
            
            except Exception as e:
                # Network or other error
                with self.lock:
                    self.stats['failed_requests'] += 1
                    self.error_counts[domain] += 1
                
                if not self._should_retry(None, e):
                    self.logger.error(f"Non-retryable error for {url}: {e}")
                    raise
                
                if attempt < self.max_retries:
                    self.logger.warning(f"Error for {url}: {e}, retrying (attempt {attempt + 1})")
                    self._update_domain_delay(domain, False, 0.0)
                    continue
                else:
                    self.logger.error(f"Max retries exceeded for {url}: {e}")
                    raise
        
        # This should never be reached
        raise requests.RequestException(f"Unexpected error in rate limiter for {url}")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get rate limiter statistics.
        
        Returns:
            Dict: Statistics including success rate, delays, etc.
        """
        with self.lock:
            total_requests = self.stats['total_requests']
            success_rate = (self.stats['successful_requests'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_requests': total_requests,
                'successful_requests': self.stats['successful_requests'],
                'failed_requests': self.stats['failed_requests'],
                'retries': self.stats['retries'],
                'rate_limit_hits': self.stats['rate_limit_hits'],
                'success_rate_percent': round(success_rate, 2),
                'total_delay_time_seconds': round(self.stats['total_delay_time'], 2),
                'average_delay_per_request': round(
                    self.stats['total_delay_time'] / max(total_requests, 1), 3
                ),
                'domain_delays': dict(self.domain_delays),
                'domain_request_counts': dict(self.request_counts),
                'domain_error_counts': dict(self.error_counts)
            }
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        with self.lock:
            self.stats = {
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'retries': 0,
                'rate_limit_hits': 0,
                'total_delay_time': 0.0
            }
            self.request_counts.clear()
            self.error_counts.clear()
    
    def set_domain_delay(self, domain: str, delay: float) -> None:
        """
        Set custom delay for a specific domain.
        
        Args:
            domain (str): Domain to set delay for
            delay (float): Delay in seconds
        """
        with self.lock:
            self.domain_delays[domain] = delay
            self.logger.info(f"Set custom delay for {domain}: {delay}s")


# Global rate limiter instance
_rate_limiter = None

def get_rate_limiter(default_delay: float = 1.0, 
                    max_retries: int = 3,
                    backoff_factor: float = 2.0) -> RateLimiter:
    """
    Get the global rate limiter instance.
    
    Args:
        default_delay (float): Default delay between requests
        max_retries (int): Maximum retry attempts
        backoff_factor (float): Exponential backoff factor
        
    Returns:
        RateLimiter: Global rate limiter instance
    """
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter(default_delay, max_retries, backoff_factor)
    return _rate_limiter


def rate_limited(delay: float = 1.0, max_retries: int = 3, 
                backoff_factor: float = 2.0):
    """
    Decorator for rate-limited HTTP requests.
    
    Args:
        delay (float): Delay between requests
        max_retries (int): Maximum retry attempts
        backoff_factor (float): Exponential backoff factor
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            rate_limiter = get_rate_limiter(delay, max_retries, backoff_factor)
            
            # If the function takes a URL parameter, use rate limiting
            if 'url' in kwargs:
                url = kwargs['url']
                rate_limiter.wait_if_needed(url)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


class RequestSession:
    """
    Enhanced requests session with built-in rate limiting and caching.
    """
    
    def __init__(self, rate_limiter: Optional[RateLimiter] = None,
                 cache_manager = None):
        """
        Initialize the request session.
        
        Args:
            rate_limiter: Rate limiter instance
            cache_manager: Cache manager instance
        """
        self.session = requests.Session()
        self.rate_limiter = rate_limiter or get_rate_limiter()
        self.cache_manager = cache_manager
        self.logger = logger
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; NFL-Data-Scraper/1.0)'
        })
    
    def get(self, url: str, use_cache: bool = True, cache_ttl: int = 3600, 
            **kwargs) -> requests.Response:
        """
        Make a GET request with rate limiting and optional caching.
        
        Args:
            url (str): URL to request
            use_cache (bool): Whether to use caching
            cache_ttl (int): Cache TTL in seconds
            **kwargs: Additional arguments for requests
            
        Returns:
            requests.Response: HTTP response
        """
        # Check cache first
        if use_cache and self.cache_manager:
            cached_response = self.cache_manager.get('http_responses', url, ttl=cache_ttl)
            if cached_response:
                self.logger.debug(f"Cache hit for {url}")
                return cached_response
        
        # Make rate-limited request
        response = self.rate_limiter.make_request(url, 'GET', self.session, **kwargs)
        
        # Cache successful responses
        if use_cache and self.cache_manager and response.status_code < 400:
            self.cache_manager.set('http_responses', url, response, ttl=cache_ttl)
        
        return response
    
    def post(self, url: str, **kwargs) -> requests.Response:
        """Make a POST request with rate limiting."""
        return self.rate_limiter.make_request(url, 'POST', self.session, **kwargs)
    
    def close(self):
        """Close the session."""
        self.session.close()


if __name__ == "__main__":
    # Example usage and testing
    rate_limiter = RateLimiter(default_delay=0.5, max_retries=2)
    
    # Test rate limiting
    test_urls = [
        'https://httpbin.org/delay/1',
        'https://httpbin.org/status/200',
        'https://httpbin.org/status/429'  # Rate limit response
    ]
    
    for url in test_urls:
        try:
            print(f"Testing {url}")
            response = rate_limiter.make_request(url, timeout=5)
            print(f"Success: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
    
    # Print statistics
    stats = rate_limiter.get_stats()
    print(f"Rate limiter stats: {stats}") 