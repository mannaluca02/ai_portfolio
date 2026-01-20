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

        # Skip rate limiting for health check, docs, and data endpoints (not chat)
        skip_paths = [
            "/api/health", "/", "/docs", "/redoc", "/openapi.json",
            "/api/contact-info", "/api/social-links", "/api/work-experiences",
            "/api/projects", "/api/skills", "/api/certificates", "/api/education"
        ]
        if request.url.path in skip_paths:
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

        # Skip rate limiting for health check, docs, and data endpoints (not chat)
        skip_paths = [
            "/api/health", "/", "/docs", "/redoc", "/openapi.json",
            "/api/contact-info", "/api/social-links", "/api/work-experiences",
            "/api/projects", "/api/skills", "/api/certificates", "/api/education"
        ]
        if request.url.path in skip_paths:
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


class DailyMonthlyRateLimiter(BaseHTTPMiddleware):
    """
    Advanced rate limiter with daily and monthly limits per IP and mode.

    Tracks requests per IP per chat mode with both daily and monthly caps.
    Resets counters automatically at the start of each day/month.
    """

    def __init__(
        self,
        app,
        mode_limits: Dict[str, Dict[str, int]]
    ):
        """
        Initialize daily/monthly rate limiter

        Args:
            app: FastAPI application
            mode_limits: Dict mapping mode to {'daily': N, 'monthly': M}
                Example: {
                    'natural': {'daily': 20, 'monthly': 100},
                    'listen': {'daily': 40, 'monthly': 200}
                }
        """
        super().__init__(app)
        self.mode_limits = mode_limits

        # Storage structure: {ip: {mode: {'daily': {...}, 'monthly': {...}}}}
        # Each period has: {'count': int, 'reset_time': datetime}
        self.usage: Dict[str, Dict[str, Dict[str, Dict]]] = defaultdict(
            lambda: defaultdict(lambda: {
                'daily': {'count': 0, 'reset_time': self._get_next_day_reset()},
                'monthly': {'count': 0, 'reset_time': self._get_next_month_reset()}
            })
        )

        logger.info(f"Daily/Monthly rate limiter initialized with limits: {mode_limits}")

    def _get_next_day_reset(self) -> datetime:
        """Get the next day reset time (midnight)"""
        now = datetime.now()
        next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        return next_day

    def _get_next_month_reset(self) -> datetime:
        """Get the next month reset time (first day of next month)"""
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return next_month

    async def dispatch(self, request: Request, call_next):
        """Process request with daily/monthly rate limiting"""

        # Skip rate limiting for non-chat endpoints
        skip_paths = [
            "/api/health", "/", "/docs", "/redoc", "/openapi.json",
            "/api/contact-info", "/api/social-links", "/api/work-experiences",
            "/api/projects", "/api/skills", "/api/certificates", "/api/education",
            "/api/chat/modes"  # Allow mode info endpoint
        ]
        if request.url.path in skip_paths:
            return await call_next(request)

        # Only apply to chat endpoint
        if not request.url.path.startswith("/api/chat"):
            return await call_next(request)

        # Get client IP
        client_ip = self._get_client_ip(request)

        # Determine mode from request body (need to read and restore body)
        mode = await self._extract_mode_from_request(request)

        # Check rate limits
        if not self._check_rate_limit(client_ip, mode):
            daily_limit = self.mode_limits.get(mode, {}).get('daily', 0)
            monthly_limit = self.mode_limits.get(mode, {}).get('monthly', 0)

            logger.warning(
                f"Rate limit exceeded for IP {client_ip} in {mode} mode. "
                f"Limits: {daily_limit}/day, {monthly_limit}/month"
            )

            raise RateLimitExceeded(retry_after=3600)  # Retry after 1 hour

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        usage = self.usage[client_ip][mode]
        daily_remaining = self.mode_limits[mode]['daily'] - usage['daily']['count']
        monthly_remaining = self.mode_limits[mode]['monthly'] - usage['monthly']['count']

        response.headers["X-RateLimit-Daily-Limit"] = str(self.mode_limits[mode]['daily'])
        response.headers["X-RateLimit-Daily-Remaining"] = str(max(0, daily_remaining))
        response.headers["X-RateLimit-Monthly-Limit"] = str(self.mode_limits[mode]['monthly'])
        response.headers["X-RateLimit-Monthly-Remaining"] = str(max(0, monthly_remaining))

        return response

    async def _extract_mode_from_request(self, request: Request) -> str:
        """Extract mode from request body"""
        try:
            # Read body
            body = await request.body()

            # Parse JSON
            import json
            data = json.loads(body) if body else {}
            mode = data.get('mode', 'natural')  # Default to natural

            # Restore body for downstream handlers
            async def receive():
                return {"type": "http.request", "body": body}

            request._receive = receive

            return mode
        except Exception as e:
            logger.warning(f"Failed to extract mode from request: {e}")
            return 'natural'  # Default to natural on error

    def _check_rate_limit(self, client_ip: str, mode: str) -> bool:
        """
        Check if request is allowed based on daily and monthly limits

        Args:
            client_ip: Client IP address
            mode: Chat mode (natural or listen)

        Returns:
            bool: True if request is allowed, False otherwise
        """
        now = datetime.now()

        # Get or initialize usage for this IP/mode
        if mode not in self.usage[client_ip]:
            self.usage[client_ip][mode] = {
                'daily': {'count': 0, 'reset_time': self._get_next_day_reset()},
                'monthly': {'count': 0, 'reset_time': self._get_next_month_reset()}
            }

        usage = self.usage[client_ip][mode]

        # Reset daily counter if needed
        if now >= usage['daily']['reset_time']:
            usage['daily'] = {'count': 0, 'reset_time': self._get_next_day_reset()}

        # Reset monthly counter if needed
        if now >= usage['monthly']['reset_time']:
            usage['monthly'] = {'count': 0, 'reset_time': self._get_next_month_reset()}

        # Check limits
        if mode not in self.mode_limits:
            logger.warning(f"No rate limits configured for mode: {mode}")
            return True  # Allow if no limits configured

        daily_limit = self.mode_limits[mode]['daily']
        monthly_limit = self.mode_limits[mode]['monthly']

        # Check if either limit is exceeded
        if usage['daily']['count'] >= daily_limit:
            logger.info(f"Daily limit exceeded for {client_ip} in {mode} mode: {usage['daily']['count']}/{daily_limit}")
            return False

        if usage['monthly']['count'] >= monthly_limit:
            logger.info(f"Monthly limit exceeded for {client_ip} in {mode} mode: {usage['monthly']['count']}/{monthly_limit}")
            return False

        # Increment counters
        usage['daily']['count'] += 1
        usage['monthly']['count'] += 1

        logger.debug(
            f"Rate limit check passed for {client_ip} in {mode} mode. "
            f"Daily: {usage['daily']['count']}/{daily_limit}, "
            f"Monthly: {usage['monthly']['count']}/{monthly_limit}"
        )

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

    def cleanup_old_entries(self, max_age_days: int = 60):
        """
        Cleanup old entries from usage tracking

        Args:
            max_age_days: Maximum age in days before cleanup
        """
        now = datetime.now()
        cutoff = now - timedelta(days=max_age_days)

        old_ips = []
        for ip, modes in self.usage.items():
            # Check if all modes for this IP are old
            all_old = all(
                mode_data['monthly']['reset_time'] < cutoff
                for mode_data in modes.values()
            )
            if all_old:
                old_ips.append(ip)

        for ip in old_ips:
            del self.usage[ip]

        if old_ips:
            logger.info(f"Cleaned up {len(old_ips)} old rate limit entries")

    def get_usage_stats(self, client_ip: str) -> Dict[str, Dict]:
        """
        Get usage statistics for a specific IP

        Args:
            client_ip: Client IP address

        Returns:
            Dict with usage stats per mode
        """
        if client_ip not in self.usage:
            return {}

        stats = {}
        for mode, usage in self.usage[client_ip].items():
            stats[mode] = {
                'daily': {
                    'used': usage['daily']['count'],
                    'limit': self.mode_limits.get(mode, {}).get('daily', 0),
                    'remaining': max(0, self.mode_limits.get(mode, {}).get('daily', 0) - usage['daily']['count']),
                    'resets_at': usage['daily']['reset_time'].isoformat()
                },
                'monthly': {
                    'used': usage['monthly']['count'],
                    'limit': self.mode_limits.get(mode, {}).get('monthly', 0),
                    'remaining': max(0, self.mode_limits.get(mode, {}).get('monthly', 0) - usage['monthly']['count']),
                    'resets_at': usage['monthly']['reset_time'].isoformat()
                }
            }

        return stats
