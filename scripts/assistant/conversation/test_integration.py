#!/usr/bin/env python3
"""
Test script to verify AIEngine integration with ConversationManager.

This script tests the enhanced functionality while ensuring backward compatibility.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from scripts.assistant.ai_engine import AIEngine
from scripts.assistant.conversation.manager import ConversationManager
from scripts.assistant.datastore import Datastore

def test_basic_integration():
    """Test basic integration between ConversationManager and AIEngine."""
    print("Testing basic AIEngine integration...")
    
    # Initialize components
    ai_engine = AIEngine()
    datastore = Datastore()
    manager = ConversationManager(ai_engine, datastore)
    
    # Test conversation history format
    test_history = [
        {"role": "user", "content": "I want to build a web application for managing tasks"},
        {"role": "assistant", "content": "What features would you like to include?"},
        {"role": "user", "content": "User authentication, task creation, and notifications"}
    ]
    
    # Test generate_response method (backward compatibility)
    try:
        response = ai_engine.generate_response(test_history)
        print(f"✅ generate_response works: {response[:50]}...")
    except Exception as e:
        print(f"❌ generate_response failed: {e}")
        return False
    
    # Test analyze_and_summarize method
    try:
        analysis_result = ai_engine.analyze_and_summarize(test_history, "summarization")
        print(f"✅ analyze_and_summarize works")
        print(f"   Summary: {analysis_result['summary'][:50]}...")
        print(f"   Confidence: {analysis_result['confidence']:.2%}")
    except Exception as e:
        print(f"❌ analyze_and_summarize failed: {e}")
        return False
    
    # Test ConversationManager's enhanced summarize_idea method
    try:
        manager.conversation_history = test_history
        summary = manager.summarize_idea()
        print(f"✅ Enhanced summarize_idea works: {summary[:50]}...")
    except Exception as e:
        print(f"❌ Enhanced summarize_idea failed: {e}")
        return False
    
    return True

def test_analysis_types():
    """Test different analysis types."""
    print("\nTesting different analysis types...")
    
    ai_engine = AIEngine()
    test_history = [
        {"role": "user", "content": "I need to build a secure e-commerce platform with user authentication, payment processing, and inventory management"}
    ]
    
    analysis_types = ["requirement_extraction", "tech_recommendation", "risk_assessment"]
    
    for analysis_type in analysis_types:
        try:
            result = ai_engine.analyze_and_summarize(test_history, analysis_type)
            print(f"✅ {analysis_type}: {result['summary'][:50]}...")
        except Exception as e:
            print(f"❌ {analysis_type} failed: {e}")
            return False
    
    return True

def test_analysis_request_detection():
    """Test analysis request detection in ConversationManager."""
    print("\nTesting analysis request detection...")
    
    ai_engine = AIEngine()
    datastore = Datastore()
    manager = ConversationManager(ai_engine, datastore)
    
    test_inputs = [
        ("Can you analyze our discussion?", True, "summarization"),
        ("Please extract the requirements", True, "requirement_extraction"),
        ("What technology would you recommend?", True, "tech_recommendation"),
        ("Are there any risks we should consider?", True, "risk_assessment"),
        ("That sounds good to me", False, "summarization"),
    ]
    
    for user_input, expected_is_analysis, expected_type in test_inputs:
        is_analysis = manager._is_analysis_request(user_input)
        analysis_type = manager._determine_analysis_type(user_input)
        
        if is_analysis == expected_is_analysis and analysis_type == expected_type:
            print(f"✅ '{user_input}' -> Analysis: {is_analysis}, Type: {analysis_type}")
        else:
            print(f"❌ '{user_input}' -> Expected Analysis: {expected_is_analysis}, Got: {is_analysis}")
            print(f"    Expected Type: {expected_type}, Got: {analysis_type}")
            return False
    
    return True

def main():
    """Run all integration tests."""
    print("🚀 Starting AIEngine Integration Tests")
    print("=" * 50)
    
    tests = [
        test_basic_integration,
        test_analysis_types,
        test_analysis_request_detection
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
                print(f"✅ {test.__name__} PASSED")
            else:
                failed += 1
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            failed += 1
            print(f"❌ {test.__name__} FAILED with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! AIEngine integration is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
