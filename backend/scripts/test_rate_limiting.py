"""
Test Rate Limiting
Verify that daily and monthly rate limits work correctly
"""
import requests
import time
from typing import Dict


API_URL = "http://localhost:8000/api/chat"


def print_rate_limits(response: requests.Response, request_num: int):
    """Print rate limit information from response headers"""
    print(f"\n--- Request #{request_num} ---")
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        print("✓ Request succeeded")
    elif response.status_code == 429:
        print("✗ Rate limit exceeded")

    # Print rate limit headers
    headers = {
        'Daily Limit': response.headers.get('X-RateLimit-Daily-Limit', 'N/A'),
        'Daily Remaining': response.headers.get('X-RateLimit-Daily-Remaining', 'N/A'),
        'Monthly Limit': response.headers.get('X-RateLimit-Monthly-Limit', 'N/A'),
        'Monthly Remaining': response.headers.get('X-RateLimit-Monthly-Remaining', 'N/A'),
    }

    print(f"Rate Limits:")
    for key, value in headers.items():
        print(f"  {key}: {value}")


def test_natural_mode():
    """Test Natural Mode rate limiting"""
    print("\n" + "="*60)
    print("TESTING NATURAL MODE RATE LIMITING")
    print("Expected: 20 requests/day, 100 requests/month")
    print("="*60)

    for i in range(3):
        try:
            response = requests.post(
                API_URL,
                json={"message": f"Test message {i+1}", "mode": "natural"},
                headers={"Content-Type": "application/json"}
            )
            print_rate_limits(response, i+1)

            # Small delay between requests
            if i < 2:
                time.sleep(0.5)

        except Exception as e:
            print(f"Error on request {i+1}: {e}")


def test_listen_mode():
    """Test Listen Mode rate limiting"""
    print("\n" + "="*60)
    print("TESTING LISTEN MODE RATE LIMITING")
    print("Expected: 40 requests/day, 200 requests/month")
    print("="*60)

    for i in range(3):
        try:
            response = requests.post(
                API_URL,
                json={"message": f"Test message {i+1}", "mode": "listen"},
                headers={"Content-Type": "application/json"}
            )
            print_rate_limits(response, i+1)

            # Small delay between requests
            if i < 2:
                time.sleep(0.5)

        except Exception as e:
            print(f"Error on request {i+1}: {e}")


def test_mixed_modes():
    """Test that different modes have separate counters"""
    print("\n" + "="*60)
    print("TESTING MIXED MODE REQUESTS")
    print("Verify that Natural and Listen modes are tracked separately")
    print("="*60)

    modes = ['natural', 'listen', 'natural', 'listen']

    for i, mode in enumerate(modes):
        try:
            response = requests.post(
                API_URL,
                json={"message": f"Mixed test {i+1}", "mode": mode},
                headers={"Content-Type": "application/json"}
            )
            print(f"\n--- {mode.upper()} Mode Request #{i+1} ---")
            print_rate_limits(response, i+1)

            if i < len(modes) - 1:
                time.sleep(0.5)

        except Exception as e:
            print(f"Error on request {i+1}: {e}")


def main():
    """Run all rate limiting tests"""
    print("\n" + "="*60)
    print("RATE LIMITING TEST SUITE")
    print("="*60)
    print("\nThis script tests the dual-period rate limiter")
    print("(daily + monthly limits per IP per mode)")
    print("\nMake sure the backend is running on http://localhost:8000")

    try:
        # Check if backend is running
        response = requests.get("http://localhost:8000/api/health")
        if response.status_code != 200:
            print("\n❌ Backend is not responding correctly")
            return
        print("\n✓ Backend is running")
    except Exception as e:
        print(f"\n❌ Cannot connect to backend: {e}")
        return

    # Run tests
    test_natural_mode()
    test_listen_mode()
    test_mixed_modes()

    print("\n" + "="*60)
    print("TEST SUITE COMPLETED")
    print("="*60)
    print("\nNotes:")
    print("- Counters decrement with each successful request")
    print("- Daily counters reset at midnight")
    print("- Monthly counters reset on the 1st of each month")
    print("- Each mode (natural/listen) has independent counters")
    print("- Rate limits are tracked per IP address")


if __name__ == "__main__":
    main()
