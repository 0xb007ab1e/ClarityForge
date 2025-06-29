#!/usr/bin/env python3
"""
Basic tests for the AI Engine Service
"""

import requests
import json
import sys
import time

def test_health_endpoint(base_url):
    """Test the health endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-engine"
        print("✓ Health endpoint working")
        return True
    except Exception as e:
        print(f"✗ Health endpoint failed: {e}")
        return False

def test_models_endpoint(base_url):
    """Test the models endpoint"""
    print("Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/ai-engine/models")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "data" in data
        assert "models" in data["data"]
        print(f"✓ Models endpoint working, found {len(data['data']['models'])} models")
        return True
    except Exception as e:
        print(f"✗ Models endpoint failed: {e}")
        return False

def test_analyze_endpoint(base_url):
    """Test the analyze endpoint"""
    print("Testing analyze endpoint...")
    try:
        payload = {
            "content": "def hello_world(): print('Hello, World!')",
            "analysis_type": "code_review",
            "model": "google/flan-t5-base"
        }
        
        response = requests.post(
            f"{base_url}/ai-engine/analyze",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success"
            assert "data" in data
            assert "analysis_id" in data["data"]
            print("✓ Analyze endpoint working")
            return True
        else:
            print(f"✗ Analyze endpoint failed with status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Analyze endpoint failed: {e}")
        return False

def main():
    """Main test function"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8002"  # Default docker-compose port
    
    print(f"Testing AI Engine Service at {base_url}")
    print("=" * 50)
    
    # Wait a bit for service to start up
    print("Waiting for service to start...")
    time.sleep(2)
    
    tests = [
        test_health_endpoint,
        test_models_endpoint,
        test_analyze_endpoint
    ]
    
    results = []
    for test in tests:
        result = test(base_url)
        results.append(result)
        time.sleep(1)  # Small delay between tests
    
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
