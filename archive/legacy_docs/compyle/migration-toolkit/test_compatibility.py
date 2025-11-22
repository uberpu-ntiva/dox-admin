#!/usr/bin/env python3
"""
Compatibility Testing Tool
Tests compatibility between Flask and FastAPI implementations
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any
import argparse

class CompatibilityTester:
    """Test compatibility between Flask and FastAPI services"""

    def __init__(self, flask_url: str, fastapi_url: str):
        self.flask_url = flask_url.rstrip('/')
        self.fastapi_url = fastapi_url.rstrip('/')

    async def run_compatibility_tests(self) -> None:
        """Run all compatibility tests"""
        print("Running compatibility tests between Flask and FastAPI...")
        print()

        # Test basic functionality
        await self._test_basic_functionality()

        # Test API patterns
        await self._test_api_patterns()

        # Test error handling
        await self._test_error_handling()

        # Test performance
        await self._test_performance()

        print("\n" + "="*60)
        print("Compatibility Testing Complete")
        print("="*60)

    async def _test_basic_functionality(self) -> None:
        """Test basic functionality"""
        print("Testing basic functionality...")

        endpoints = [
            ("GET", "/"),
            ("GET", "/health"),
            ("GET", "/docs"),
            ("GET", "/openapi.json")
        ]

        for method, path in endpoints:
            await self._compare_endpoints(method, path)

    async def _test_api_patterns(self) -> None:
        """Test common API patterns"""
        print("\nTesting API patterns...")

        # Test query parameters
        await self._test_query_parameters()

        # Test path parameters
        await self._test_path_parameters()

        # Test request body
        await self._test_request_body()

    async def _test_query_parameters(self) -> None:
        """Test query parameter handling"""
        print("  Testing query parameters...")

        test_cases = [
            "/health?format=json",
            "/health?verbose=true",
            "/health?format=json&verbose=true"
        ]

        for path in test_cases:
            await self._compare_endpoints("GET", path)

    async def _test_path_parameters(self) -> None:
        """Test path parameter handling"""
        print("  Testing path parameters...")

        # Note: These would need actual endpoints with path parameters
        # For now, just test that FastAPI handles them correctly
        await self._compare_endpoints("GET", "/health")  # Basic test

    async def _test_request_body(self) -> None:
        """Test request body handling"""
        print("  Testing request body...")

        test_data = {
            "test": "data",
            "number": 123,
            "array": [1, 2, 3]
        }

        # Test with an endpoint that accepts POST
        try:
            await self._compare_endpoints("POST", "/health", test_data)
        except Exception as e:
            print(f"    ⚠️ POST test failed (expected for health endpoint): {e}")

    async def _test_error_handling(self) -> None:
        """Test error handling"""
        print("\nTesting error handling...")

        # Test 404 errors
        await self._compare_endpoints("GET", "/nonexistent")

        # Test method not allowed
        await self._compare_endpoints("PATCH", "/health")

        # Test invalid request body
        invalid_data = "invalid json"
        try:
            await self._compare_endpoints("POST", "/health", invalid_data)
        except Exception as e:
            print(f"    ⚠️ Invalid body test failed (expected): {e}")

    async def _test_performance(self) -> None:
        """Test performance comparison"""
        print("\nTesting performance...")

        # Single request performance
        flask_time = await self._measure_response_time(self.flask_url + "/health")
        fastapi_time = await self._measure_response_time(self.fastapi_url + "/health")

        print(f"  Flask response time: {flask_time:.3f}s")
        print(f"  FastAPI response time: {fastapi_time:.3f}s")

        if flask_time > 0 and fastapi_time > 0:
            improvement = ((flask_time - fastapi_time) / flask_time) * 100
            if improvement > 0:
                print(f"  ✅ FastAPI is {improvement:.1f}% faster")
            else:
                print(f"  ⚠️ FastAPI is {abs(improvement):.1f}% slower")

        # Concurrent request test
        await self._test_concurrent_requests()

    async def _test_concurrent_requests(self) -> None:
        """Test concurrent request handling"""
        print("  Testing concurrent requests...")

        num_requests = 10
        url = "/health"

        # Test Flask concurrent requests
        flask_times = await self._make_concurrent_requests(
            self.flask_url + url, num_requests
        )
        avg_flask_time = sum(flask_times) / len(flask_times)

        # Test FastAPI concurrent requests
        fastapi_times = await self._make_concurrent_requests(
            self.fastapi_url + url, num_requests
        )
        avg_fastapi_time = sum(fastapi_times) / len(fastapi_times)

        print(f"  Flask concurrent avg: {avg_flask_time:.3f}s")
        print(f"  FastAPI concurrent avg: {avg_fastapi_time:.3f}s")

        improvement = ((avg_flask_time - avg_fastapi_time) / avg_flask_time) * 100
        if improvement > 0:
            print(f"  ✅ FastAPI is {improvement:.1f}% faster with concurrent requests")
        else:
            print(f"  ⚠️ FastAPI is {abs(improvement):.1f}% slower with concurrent requests")

    async def _compare_endpoints(self, method: str, path: str, data: Any = None) -> None:
        """Compare endpoints between Flask and FastAPI"""
        flask_result = await self._make_request(self.flask_url + path, method, data)
        fastapi_result = await self._make_request(self.fastapi_url + path, method, data)

        status_match = flask_result['status_code'] == fastapi_result['status_code']
        body_match = self._compare_bodies(flask_result, fastapi_result)

        status = "✅" if status_match and body_match else "❌"
        print(f"  {status} {method} {path}")

        if not status_match:
            print(f"    Status codes: Flask={flask_result['status_code']}, FastAPI={fastapi_result['status_code']}")

        if not body_match:
            print(f"    Bodies differ")

    async def _make_request(self, url: str, method: str = "GET", data: Any = None) -> Dict[str, Any]:
        """Make HTTP request"""
        async with aiohttp.ClientSession() as session:
            try:
                if method == "GET":
                    async with session.get(url) as response:
                        return await self._parse_response(response)
                elif method == "POST":
                    if isinstance(data, dict):
                        async with session.post(url, json=data) as response:
                            return await self._parse_response(response)
                    else:
                        async with session.post(url, data=data) as response:
                            return await self._parse_response(response)
                elif method == "PATCH":
                    async with session.patch(url, json=data) as response:
                        return await self._parse_response(response)
                else:
                    return {'status_code': 405, 'body': 'Method not allowed'}

            except Exception as e:
                return {'status_code': 500, 'body': str(e)}

    async def _parse_response(self, response) -> Dict[str, Any]:
        """Parse HTTP response"""
        content = await response.text()
        try:
            body = json.loads(content)
        except json.JSONDecodeError:
            body = content

        return {
            'status_code': response.status,
            'body': body,
            'headers': dict(response.headers)
        }

    def _compare_bodies(self, flask_result: Dict[str, Any], fastapi_result: Dict[str, Any]) -> bool:
        """Compare response bodies"""
        flask_body = flask_result.get('body', {})
        fastapi_body = fastapi_result.get('body', {})

        # Both are strings
        if isinstance(flask_body, str) and isinstance(fastapi_body, str):
            return flask_body == fastapi_body

        # Both are dictionaries
        if isinstance(flask_body, dict) and isinstance(fastapi_body, dict):
            # Ignore timing fields
            ignore_keys = {'timestamp', 'response_time', 'X-Process-Time'}

            flask_keys = set(flask_body.keys()) - ignore_keys
            fastapi_keys = set(fastapi_body.keys()) - ignore_keys

            if flask_keys != fastapi_keys:
                return False

            for key in flask_keys:
                if key in flask_body and key in fastapi_body:
                    if flask_body[key] != fastapi_body[key]:
                        return False

            return True

        return False

    async def _make_concurrent_requests(self, url: str, num_requests: int) -> List[float]:
        """Make concurrent requests and measure response times"""
        async def single_request():
            start = time.time()
            await self._make_request(url)
            return time.time() - start

        tasks = [single_request() for _ in range(num_requests)]
        return await asyncio.gather(*tasks)

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test Flask to FastAPI compatibility")
    parser.add_argument("--flask-url", default="http://localhost:5000", help="Flask app URL")
    parser.add_argument("--fastapi-url", default="http://localhost:8000", help="FastAPI app URL")

    args = parser.parse_args()

    tester = CompatibilityTester(args.flask_url, args.fastapi_url)
    await tester.run_compatibility_tests()

if __name__ == "__main__":
    asyncio.run(main())