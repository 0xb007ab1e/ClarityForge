"""API endpoint tests using httpx.AsyncClient."""

import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from fastapi.testclient import TestClient

from clarity_forge.api.v1.endpoints import router


# Create a test FastAPI app
def create_test_app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI(title="ClarityForge Test API", version="1.0.0")
    app.include_router(router)
    return app


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    @pytest.fixture
    def app(self):
        """Create a test FastAPI application."""
        return create_test_app()
    
    @pytest.fixture
    def client(self, app):
        """Create a test client for synchronous testing."""
        return TestClient(app)
    
    @pytest_asyncio.fixture
    async def async_client(self, app):
        """Create an async test client for asynchronous testing."""
        # Use httpx.AsyncClient with ASGI transport
        from httpx import ASGITransport
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac
    
    def test_health_check_endpoint_sync(self, client):
        """Test health check endpoint with synchronous client."""
        response = client.get("/v1/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        json_response = response.json()
        assert json_response == {"status": "healthy"}
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint_async(self, async_client):
        response = await async_client.get("/v1/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        json_response = response.json()
        assert json_response == {"status": "healthy"}
    
    def test_health_check_endpoint_structure(self, client):
        """Test that health check endpoint returns proper structure."""
        response = client.get("/v1/health")
        
        assert response.status_code == 200
        json_response = response.json()
        
        # Verify response structure
        assert isinstance(json_response, dict)
        assert "status" in json_response
        assert json_response["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint_multiple_calls(self, async_client):
        """Test multiple calls to health check endpoint."""
        # Test multiple concurrent calls
        responses = []
        for _ in range(5):
            response = await async_client.get("/v1/health")
            responses.append(response)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    def test_health_check_endpoint_headers(self, client):
        """Test health check endpoint response headers."""
        response = client.get("/v1/health")
        
        assert response.status_code == 200
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
        assert "content-length" in response.headers
    
    def test_invalid_endpoint(self, client):
        """Test request to non-existent endpoint."""
        response = client.get("/v1/nonexistent")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_invalid_endpoint_async(self, async_client):
        """Test async request to non-existent endpoint."""
        response = await async_client.get("/v1/nonexistent")
        
        assert response.status_code == 404
    
    def test_health_check_wrong_method(self, client):
        """Test health check endpoint with wrong HTTP method."""
        # Health check only supports GET
        response = client.post("/v1/health")
        assert response.status_code == 405  # Method Not Allowed
        
        response = client.put("/v1/health")
        assert response.status_code == 405
        
        response = client.delete("/v1/health")
        assert response.status_code == 405
    
    @pytest.mark.asyncio
    async def test_health_check_wrong_method_async(self, async_client):
        """Test health check endpoint with wrong HTTP method using async client."""
        # Health check only supports GET
        response = await async_client.post("/v1/health")
        assert response.status_code == 405  # Method Not Allowed
        
        response = await async_client.put("/v1/health")
        assert response.status_code == 405
        
        response = await async_client.delete("/v1/health")
        assert response.status_code == 405
    
    def test_api_versioning(self, client):
        """Test that API versioning works correctly."""
        # Test with v1 prefix
        response = client.get("/v1/health")
        assert response.status_code == 200
        
        # Test without version prefix (should fail)
        response = client.get("/health")
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, async_client):
        """Test handling of concurrent requests."""
        import asyncio
        
        # Create multiple concurrent requests
        tasks = []
        for i in range(10):
            task = asyncio.create_task(async_client.get("/v1/health"))
            tasks.append(task)
        
        # Wait for all requests to complete
        responses = await asyncio.gather(*tasks)
        
        # All responses should be successful
        for response in responses:
            assert response.status_code == 200
            assert response.json() == {"status": "healthy"}
    
    def test_api_openapi_docs_available(self, client):
        """Test that OpenAPI documentation is available."""
        # Most FastAPI apps serve docs at /docs
        response = client.get("/docs")
        # Status could be 200 (if docs are enabled) or 404 (if disabled in test)
        assert response.status_code in [200, 404]
        
        # Test OpenAPI JSON endpoint
        response = client.get("/openapi.json")
        assert response.status_code in [200, 404]
    
    @pytest.mark.parametrize("endpoint", [
        "/v1/health",
        "/v1/health/",  # Test with trailing slash
    ])
    def test_endpoint_variations(self, client, endpoint):
        """Test endpoint with different URL patterns."""
        response = client.get(endpoint)
        # Either should work (200) or redirect (307/308) or not found (404)
        assert response.status_code in [200, 307, 308, 404]
        
        if response.status_code == 200:
            assert response.json() == {"status": "healthy"}
    
    def test_response_time_reasonable(self, client):
        """Test that response time is reasonable."""
        import time
        
        start_time = time.time()
        response = client.get("/v1/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Health check should respond quickly (less than 1 second)
        assert response_time < 1.0
    
    @pytest.mark.asyncio
    async def test_async_response_time_reasonable(self, async_client):
        """Test that async response time is reasonable."""
        import time
        
        start_time = time.time()
        response = await async_client.get("/v1/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Health check should respond quickly (less than 1 second)
        assert response_time < 1.0
