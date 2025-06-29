#!/usr/bin/env python3
"""
End-to-end integration test script for ClarityForge services.

This script verifies that both the main API (clarity-forge) and agent_sandbox
are healthy and responsive by making concurrent HTTP requests.
"""

import asyncio
import aiohttp
import json
import time
import sys
from datetime import datetime
from typing import Dict, Any, Optional

# Service configuration
MAIN_API_URL = "http://localhost:8000"
AGENT_SANDBOX_URL = "http://localhost:8001"

# Test timeout in seconds
REQUEST_TIMEOUT = 30
HEALTH_CHECK_INTERVAL = 2


class HealthCheckResult:
    """Container for health check results."""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.is_healthy = False
        self.response_time_ms = 0
        self.status_code = None
        self.error_message = None
        self.response_data = None
        self.timestamp = datetime.now()


async def check_service_health(session: aiohttp.ClientSession, 
                             service_name: str, 
                             base_url: str,
                             endpoint: str = "/health",
                             method: str = "GET",
                             payload: dict = None) -> HealthCheckResult:
    """
    Check the health of a service by making an HTTP request.
    
    Args:
        session: aiohttp client session
        service_name: Name of the service for logging
        base_url: Base URL of the service
        endpoint: Health check endpoint (defaults to /health)
        method: HTTP method (GET or POST)
        payload: JSON payload for POST requests
        
    Returns:
        HealthCheckResult object with test results
    """
    result = HealthCheckResult(service_name)
    url = f"{base_url}{endpoint}"
    
    try:
        start_time = time.time()
        
        if method.upper() == "POST":
            async with session.post(url, json=payload or {}, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                end_time = time.time()
                result.response_time_ms = int((end_time - start_time) * 1000)
                result.status_code = response.status
                
                # Try to parse JSON response
                try:
                    result.response_data = await response.json()
                except:
                    result.response_data = await response.text()
                
                # Consider 2xx status codes as healthy
                result.is_healthy = 200 <= response.status < 300
                
                if not result.is_healthy:
                    result.error_message = f"Unhealthy status code: {response.status}"
        else:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
                end_time = time.time()
                result.response_time_ms = int((end_time - start_time) * 1000)
                result.status_code = response.status
                
                # Try to parse JSON response
                try:
                    result.response_data = await response.json()
                except:
                    result.response_data = await response.text()
                
                # Consider 2xx status codes as healthy
                result.is_healthy = 200 <= response.status < 300
                
                if not result.is_healthy:
                    result.error_message = f"Unhealthy status code: {response.status}"
                
    except asyncio.TimeoutError:
        result.error_message = f"Request timeout after {REQUEST_TIMEOUT}s"
    except aiohttp.ClientConnectorError as e:
        result.error_message = f"Connection error: {str(e)}"
    except Exception as e:
        result.error_message = f"Unexpected error: {str(e)}"
    
    return result


async def test_main_api_functionality(session: aiohttp.ClientSession) -> HealthCheckResult:
    """
    Test main API functionality beyond basic health check.
    """
    result = HealthCheckResult("main-api-functionality")
    
    try:
        start_time = time.time()
        
        # Test a basic API endpoint - try to get available endpoints or similar
        test_url = f"{MAIN_API_URL}/docs"  # OpenAPI docs endpoint
        
        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
            end_time = time.time()
            result.response_time_ms = int((end_time - start_time) * 1000)
            result.status_code = response.status
            result.is_healthy = 200 <= response.status < 300
            
            if not result.is_healthy:
                result.error_message = f"API docs endpoint returned: {response.status}"
            else:
                result.response_data = {"message": "API docs accessible"}
                
    except Exception as e:
        result.error_message = f"API functionality test failed: {str(e)}"
    
    return result


async def test_agent_sandbox_functionality(session: aiohttp.ClientSession) -> HealthCheckResult:
    """
    Test agent sandbox functionality beyond basic health check.
    """
    result = HealthCheckResult("agent-sandbox-functionality")
    
    try:
        start_time = time.time()
        
        # Test sandbox docs endpoint
        test_url = f"{AGENT_SANDBOX_URL}/docs"
        
        async with session.get(test_url, timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)) as response:
            end_time = time.time()
            result.response_time_ms = int((end_time - start_time) * 1000)
            result.status_code = response.status
            result.is_healthy = 200 <= response.status < 300
            
            if not result.is_healthy:
                result.error_message = f"Sandbox docs endpoint returned: {response.status}"
            else:
                result.response_data = {"message": "Sandbox docs accessible"}
                
    except Exception as e:
        result.error_message = f"Sandbox functionality test failed: {str(e)}"
    
    return result


async def run_concurrent_health_checks() -> Dict[str, HealthCheckResult]:
    """
    Run health checks for both services concurrently.
    
    Returns:
        Dictionary mapping service names to their health check results
    """
    async with aiohttp.ClientSession() as session:
        # Create all health check tasks
        tasks = [
            check_service_health(session, "main-api", MAIN_API_URL, "/healthz"),
            check_service_health(session, "agent-sandbox", AGENT_SANDBOX_URL, "/check_alignment/", "POST", {"content": "health_check"}),
            test_main_api_functionality(session),
            test_agent_sandbox_functionality(session),
        ]
        
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        health_results = {}
        for result in results:
            if isinstance(result, Exception):
                print(f"Error in health check: {result}")
                continue
            
            health_results[result.service_name] = result
        
        return health_results


def print_health_report(results: Dict[str, HealthCheckResult]) -> bool:
    """
    Print a formatted health report and return overall health status.
    
    Args:
        results: Dictionary of health check results
        
    Returns:
        True if all services are healthy, False otherwise
    """
    print("=" * 80)
    print("CLARITYFORGE INTEGRATION TEST REPORT")
    print("=" * 80)
    print(f"Test run time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    all_healthy = True
    
    for service_name, result in results.items():
        status = "✅ HEALTHY" if result.is_healthy else "❌ UNHEALTHY"
        print(f"Service: {service_name.upper()}")
        print(f"Status: {status}")
        
        if result.status_code:
            print(f"HTTP Status: {result.status_code}")
        
        if result.response_time_ms:
            print(f"Response Time: {result.response_time_ms}ms")
        
        if result.error_message:
            print(f"Error: {result.error_message}")
            all_healthy = False
        
        if result.response_data and result.is_healthy:
            if isinstance(result.response_data, dict):
                print(f"Response: {json.dumps(result.response_data, indent=2)}")
            else:
                print(f"Response: {str(result.response_data)[:200]}...")
        
        print("-" * 40)
    
    print()
    overall_status = "✅ ALL SERVICES HEALTHY" if all_healthy else "❌ SOME SERVICES UNHEALTHY"
    print(f"Overall Status: {overall_status}")
    print("=" * 80)
    
    return all_healthy


def check_network_constraints():
    """
    Document networking and resource constraints.
    """
    print("\nNETWORK AND RESOURCE CONSTRAINTS:")
    print("-" * 40)
    print("Port Mappings:")
    print("  - Main API (clarity-forge): localhost:8000 -> container:8000")
    print("  - Agent Sandbox: localhost:8001 -> container:8000")
    print()
    print("Resource Limits (agent_sandbox):")
    print("  - CPU: 0.5 cores")
    print("  - Memory: 512MB")
    print()
    print("Network Requirements:")
    print("  - Both services must be accessible via HTTP")
    print("  - Services communicate within Docker network 'clarityforge_default'")
    print("  - External access via mapped ports on localhost")
    print()


async def wait_for_services_startup(max_wait_time: int = 60) -> bool:
    """
    Wait for services to start up and become responsive.
    
    Args:
        max_wait_time: Maximum time to wait in seconds
        
    Returns:
        True if services are ready, False if timeout
    """
    print("Waiting for services to start up...")
    
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            async with aiohttp.ClientSession() as session:
                main_api_task = check_service_health(session, "main-api", MAIN_API_URL, "/healthz")
                sandbox_task = check_service_health(session, "agent-sandbox", AGENT_SANDBOX_URL, "/check_alignment/", "POST", {"content": "health_check"})
                
                main_result, sandbox_result = await asyncio.gather(main_api_task, sandbox_task)
                
                if main_result.is_healthy and sandbox_result.is_healthy:
                    print("✅ Both services are ready!")
                    return True
                
                print(f"⏳ Waiting... Main API: {'✅' if main_result.is_healthy else '❌'}, "
                      f"Sandbox: {'✅' if sandbox_result.is_healthy else '❌'}")
                
        except Exception as e:
            print(f"⏳ Waiting for services... ({str(e)[:50]})")
        
        await asyncio.sleep(HEALTH_CHECK_INTERVAL)
    
    print("❌ Timeout waiting for services to start")
    return False


async def main():
    """
    Main function to run the integration test.
    """
    print("ClarityForge Integration Test Suite")
    print("=" * 50)
    
    # Wait for services to be ready
    if not await wait_for_services_startup():
        print("❌ Services did not start up in time")
        sys.exit(1)
    
    # Run health checks
    try:
        results = await run_concurrent_health_checks()
        
        # Print report
        all_healthy = print_health_report(results)
        
        # Document constraints
        check_network_constraints()
        
        # Exit with appropriate code
        sys.exit(0 if all_healthy else 1)
        
    except Exception as e:
        print(f"❌ Integration test failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
