"""
Mock implementation of AI models for testing purposes.
This allows testing the integration without requiring external API access.
"""

from typing import List

def generate_response(context: str) -> str:
    """Mock implementation of generate_response for testing."""
    if "summarize" in context.lower():
        return "Summary: This conversation discusses building a web application with user authentication and task management features."
    elif "requirements" in context.lower():
        return "Requirements: 1. User authentication system 2. Task creation and management 3. Notification system"
    elif "technology" in context.lower() or "tech" in context.lower():
        return "Technology recommendations: React for frontend, Node.js for backend, PostgreSQL for database"
    elif "risk" in context.lower():
        return "Risk assessment: Security vulnerabilities in authentication, scalability concerns, data privacy issues"
    else:
        return "This is a mock response based on the provided context. In a real implementation, this would be generated by an AI model."

def classify(text: str) -> List[str]:
    """Mock implementation of classification for testing."""
    text_lower = text.lower()
    labels = []
    
    if any(word in text_lower for word in ["tech", "technical", "bug", "error", "issue"]):
        labels.append("tech support")
    if any(word in text_lower for word in ["payment", "bill", "invoice", "cost", "price"]):
        labels.append("billing")
    if any(word in text_lower for word in ["buy", "purchase", "sale", "product", "demo"]):
        labels.append("sales")
    
    return labels
