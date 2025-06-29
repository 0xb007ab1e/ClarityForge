#!/usr/bin/env python3
"""
Test script for AI Engine Service Enhanced Monitoring Features

This script demonstrates the new health monitoring and error tracking capabilities
added to the AI Engine Service. It tests both the enhanced health endpoint and
the new error monitoring endpoint.

Usage:
    python test_monitoring.py [--host localhost] [--port 8000]
"""

import requests
import json
import argparse
import time
from datetime import datetime

def test_enhanced_health_endpoint(base_url):
    """Test the enhanced health endpoint."""
    print("🔍 Testing Enhanced Health Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check successful!")
            print(f"   Overall Status: {health_data.get('status', 'unknown')}")
            print(f"   Service: {health_data.get('service', 'unknown')}")
            print(f"   Timestamp: {health_data.get('timestamp', 'unknown')}")
            print()
            
            # Display component health details
            components = health_data.get('components', {})
            print("📊 Component Health Details:")
            for component_name, component_data in components.items():
                status = component_data.get('status', 'unknown')
                message = component_data.get('message', 'No message')
                
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"   {status_icon} {component_name.replace('_', ' ').title()}: {status}")
                print(f"      Message: {message}")
                
                # Display additional metrics if available
                if 'response_time_ms' in component_data:
                    print(f"      Response Time: {component_data['response_time_ms']}ms")
                if 'available_count' in component_data:
                    print(f"      Available Count: {component_data['available_count']}")
                print()
            
        else:
            print(f"❌ Health check failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to health endpoint: {e}")
    
    print()

def test_error_monitoring_endpoint(base_url):
    """Test the error monitoring endpoint."""
    print("📈 Testing Error Monitoring Endpoint...")
    print("=" * 50)
    
    try:
        response = requests.get(f"{base_url}/monitoring/errors", timeout=10)
        
        if response.status_code == 200:
            monitoring_data = response.json()
            print(f"✅ Error monitoring data retrieved successfully!")
            print(f"   Timestamp: {monitoring_data.get('timestamp', 'unknown')}")
            print()
            
            # Display error summary
            error_summary = monitoring_data.get('error_summary', {})
            print("📊 Error Summary:")
            print(f"   Total Errors: {error_summary.get('total_errors', 0)}")
            
            error_counts = error_summary.get('error_counts', {})
            if error_counts:
                print("   Error Breakdown:")
                for error_key, count in error_counts.items():
                    print(f"     - {error_key}: {count} occurrences")
            else:
                print("   ✅ No errors recorded")
            print()
            
            # Display health indicators
            health_indicators = monitoring_data.get('health_indicators', {})
            print("🎯 Health Indicators:")
            print(f"   Error Rate: {health_indicators.get('error_rate', 'unknown')}")
            print(f"   Most Frequent Error: {health_indicators.get('most_frequent_error', 'None')}")
            print(f"   Total Error Count: {health_indicators.get('total_error_count', 0)}")
            print(f"   Unique Error Types: {health_indicators.get('unique_error_types', 0)}")
            print()
            
            # Display recommendations
            recommendations = health_indicators.get('recommendations', [])
            if recommendations:
                print("💡 Recommendations:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"   {i}. {rec}")
            print()
            
            # Display recent errors (if any)
            recent_errors = error_summary.get('recent_errors', [])
            if recent_errors:
                print("🚨 Recent Errors (last 5):")
                for error in recent_errors[-5:]:
                    timestamp = error.get('timestamp', 'unknown')
                    error_type = error.get('error_type', 'unknown')
                    model_id = error.get('model_id', 'unknown')
                    message = error.get('error_message', 'No message')[:100]
                    print(f"   [{timestamp}] {error_type} - {model_id}")
                    print(f"     Message: {message}...")
                    print()
            
        else:
            print(f"❌ Error monitoring failed with status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to connect to monitoring endpoint: {e}")
    
    print()

def test_analyze_endpoint(base_url):
    """Test the analyze endpoint to potentially generate some monitored activity."""
    print("🧪 Testing Analyze Endpoint (to generate monitoring activity)...")
    print("=" * 50)
    
    test_request = {
        "content": "def hello_world(): print('Hello, World!')",
        "analysis_type": "code_review",
        "model": "google/flan-t5-base"
    }
    
    try:
        response = requests.post(
            f"{base_url}/ai-engine/analyze",
            json=test_request,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Analysis request successful!")
            print(f"   Analysis ID: {result.get('data', {}).get('analysis_id', 'unknown')}")
            print(f"   Processing Time: {result.get('data', {}).get('processing_time_ms', 'unknown')}ms")
            print(f"   Confidence: {result.get('data', {}).get('confidence', 'unknown')}")
        else:
            print(f"⚠️ Analysis request failed with status code: {response.status_code}")
            print(f"   This may generate error monitoring data")
            
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Failed to connect to analyze endpoint: {e}")
        print(f"   This may generate error monitoring data")
    
    print()

def main():
    """Main test function."""
    parser = argparse.ArgumentParser(description='Test AI Engine Service Monitoring Features')
    parser.add_argument('--host', default='localhost', help='Service host (default: localhost)')
    parser.add_argument('--port', default='8000', help='Service port (default: 8000)')
    
    args = parser.parse_args()
    base_url = f"http://{args.host}:{args.port}"
    
    print("🤖 AI Engine Service - Enhanced Monitoring Test Suite")
    print("=" * 60)
    print(f"Testing service at: {base_url}")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    test_enhanced_health_endpoint(base_url)
    test_error_monitoring_endpoint(base_url)
    test_analyze_endpoint(base_url)
    
    # Wait a moment and test monitoring again to see if analyze generated any activity
    print("⏳ Waiting 2 seconds to check for monitoring updates...")
    time.sleep(2)
    test_error_monitoring_endpoint(base_url)
    
    print("🎉 Monitoring test suite completed!")
    print()
    print("📝 Next Steps:")
    print("1. Set up environment variables for centralized monitoring (see MONITORING_CONFIG.md)")
    print("2. Configure your monitoring system to poll /health and /monitoring/errors")
    print("3. Set up alerts based on health status changes and error rates")
    print("4. Review the error monitoring data periodically for optimization opportunities")

if __name__ == "__main__":
    main()
