"""
Rate Limiting Middleware
Simple in-memory rate limiter for API endpoints
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RateLimitExceeded(HTTPException):
    """Custom exception for rate limit exceeded"""
    def __init__(self, retry_after: int):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "RateLimitExceeded",
                "message": "Rate limit exceeded. Please try again later.",
                "retry_after": retry_after
            }
        )


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware

    Implements a simple token bucket algorithm:
    - Each IP gets a certain number of tokens per time window
    - Each request consumes one token
    - Tokens refill at a constant rate
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        burst_size: int = 10
    ):
        """
        Initialize rate limiter

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (tokens bucket size)
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size
        self.refill_rate = requests_per_minute / 60.0  # Tokens per second

        # Storage: {ip: (tokens, last_refill_time)}
        self.buckets: Dict[str, Tuple[float, datetime]] = defaultdict(
            lambda: (float(burst_size), datetime.now())
        )

        logger.info(
            f"Rate limiter initialized: {requests_per_minute} req/min, "
            f"burst: {burst_size}"
        )

    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""

        # Skip rate limiting for health check and docs
        if request.url.path in ["/api/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Check rate limit
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise RateLimitExceeded(retry_after=60)

        # Continue processing
        response = await call_next(request)

        # Add rate limit headers
        tokens, _ = self.buckets[client_ip]
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(int(tokens))

        return response

    def _check_rate_limit(self, client_ip: str) -> bool:
        """
        Check if request is allowed based on rate limit

        Args:
            client_ip: Client IP address

        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = datetime.now()
        tokens, last_refill = self.buckets[client_ip]

        # Calculate tokens to add based on time passed
        time_passed = (now - last_refill).total_seconds()
        tokens_to_add = time_passed * self.refill_rate

        # Refill tokens (up to burst_size)
        tokens = min(self.burst_size, tokens + tokens_to_add)

        # Check if we have enough tokens
        if tokens < 1.0:
            return False

        # Consume one token
        tokens -= 1.0

        # Update bucket
        self.buckets[client_ip] = (tokens, now)

        return True

    def _get_client_ip(self, request: Request) -> str:
        """
        Get client IP address from request

        Args:
            request: FastAPI request

        Returns:
            str: Client IP address
        """
        # Check X-Forwarded-For header (for proxies)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()

        # Check X-Real-IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct IP
        return request.client.host if request.client else "unknown"

    def cleanup_old_entries(self, max_age_hours: int = 24):
        """
        Cleanup old entries from buckets

        Args:
            max_age_hours: Maximum age in hours before cleanup
        """
        now = datetime.now()
        cutoff = now - timedelta(hours=max_age_hours)

        old_ips = [
            ip for ip, (_, last_refill) in self.buckets.items()
            if last_refill < cutoff
        ]

        for ip in old_ips:
            del self.buckets[ip]

        if old_ips:
            logger.info(f"Cleaned up {len(old_ips)} old rate limit entries")


# Path-specific rate limits
class PathBasedRateLimiter(RateLimiterMiddleware):
    """
    Rate limiter with different limits for different paths
    """

    def __init__(self, app, limits: Dict[str, Tuple[int, int]]):
        """
        Initialize path-based rate limiter

        Args:
            app: FastAPI application
            limits: Dict mapping path prefixes to (requests_per_minute, burst_size)
        """
        super().__init__(app)
        self.limits = limits

    async def dispatch(self, request: Request, call_next):
        """Process request with path-specific rate limiting"""

        # Skip rate limiting for health check and docs
        if request.url.path in ["/api/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get path-specific limits
        path = request.url.path
        for prefix, (rpm, burst) in self.limits.items():
            if path.startswith(prefix):
                self.requests_per_minute = rpm
                self.burst_size = burst
                self.refill_rate = rpm / 60.0
                break

        # Use parent dispatch
        return await super().dispatch(request, call_next)
