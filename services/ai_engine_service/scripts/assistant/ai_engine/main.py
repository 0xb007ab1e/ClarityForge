from scripts.ai_engine.model import generate_response, classify
from functools import lru_cache
from typing import Dict, List, Tuple, Any
import time
import uuid
import logging

logger = logging.getLogger(__name__)

class AnalysisRequest:
    """Data model for analysis requests."""
    def __init__(self, content: str, analysis_type: str, model: str = None, parameters: dict = None):
        self.content = content
        self.analysis_type = analysis_type
        self.model = model
        self.parameters = parameters or {}

class AnalysisResult:
    """Data model for analysis results."""
    def __init__(self, analysis_id: str, results: dict, confidence: float, 
                 recommendations: list, processing_time_ms: int):
        self.analysis_id = analysis_id
        self.results = results
        self.confidence = confidence
        self.recommendations = recommendations
        self.processing_time_ms = processing_time_ms

class AIEngine:
    """Core AI Engine class for content analysis and processing.
    
    This class orchestrates the AI-powered analysis workflow, managing multiple
    AI models and providing various analysis capabilities. It serves as the main
    interface between the FastAPI service and the underlying AI models.
    
    The AIEngine supports multiple analysis types:
    - Code review and quality assessment
    - Requirement extraction from documents
    - Technology stack recommendations
    - Risk assessment and mitigation planning
    
    Attributes:
        supported_models (dict): Registry of available AI models with metadata
    """
    
    def __init__(self):
        """Initialize the AI Engine with supported models configuration.
        
        Sets up the registry of available AI models with their capabilities,
        providers, and metadata. This configuration determines which models
        are available for different analysis types.
        """
        # Registry of supported AI models with comprehensive metadata
        self.supported_models = {
            "google/flan-t5-base": {
                "name": "FLAN-T5 Base",
                "description": "General-purpose model for natural language understanding",
                "capabilities": ["text_generation", "question_answering", "summarization"],
                "provider": "Google",
                "version": "base"
            },
            "facebook/bart-large-mnli": {
                "name": "BART Large MNLI",
                "description": "Model for zero-shot classification and natural language inference",
                "capabilities": ["classification", "zero_shot_classification"],
                "provider": "Facebook",
                "version": "large"
            }
        }

    def analyze_content(self, req: AnalysisRequest) -> AnalysisResult:
        """Analyze content using AI models with confidence scoring and latency tracking."""
        start_time = time.time()
        analysis_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting analysis {analysis_id} for type: {req.analysis_type}")
            
            # Determine which model to use
            model_id = req.model or "google/flan-t5-base"
            if model_id not in self.supported_models:
                raise ValueError(f"Unsupported model: {model_id}")
            
            # Perform analysis based on type
            if req.analysis_type == "code_review":
                results, confidence = self._analyze_code_review(req.content, model_id)
            elif req.analysis_type == "requirement_extraction":
                results, confidence = self._analyze_requirements(req.content, model_id)
            elif req.analysis_type == "tech_recommendation":
                results, confidence = self._analyze_tech_recommendation(req.content, model_id)
            elif req.analysis_type == "risk_assessment":
                results, confidence = self._analyze_risk_assessment(req.content, model_id)
            else:
                # Default analysis
                results, confidence = self._default_analysis(req.content, model_id)
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Generate recommendations based on results
            recommendations = self._generate_recommendations(results, req.analysis_type)
            
            logger.info(f"Analysis {analysis_id} completed in {processing_time_ms}ms with confidence {confidence}")
            
            return AnalysisResult(
                analysis_id=analysis_id,
                results=results,
                confidence=confidence,
                recommendations=recommendations,
                processing_time_ms=processing_time_ms
            )
            
        except Exception as e:
            processing_time_ms = int((time.time() - start_time) * 1000)
            logger.error(f"Analysis {analysis_id} failed after {processing_time_ms}ms: {str(e)}")
            
            return AnalysisResult(
                analysis_id=analysis_id,
                results={"error": str(e), "status": "failed"},
                confidence=0.0,
                recommendations=["Review input parameters and try again"],
                processing_time_ms=processing_time_ms
            )
    
    def _analyze_code_review(self, content: str, model_id: str) -> Tuple[Dict[str, Any], float]:
        """Perform code review analysis."""
        prompt = f"Review the following code and provide feedback on quality, potential issues, and improvements:\n\n{content}"
        response = generate_response(prompt)
        
        # Calculate confidence based on response length and content quality indicators
        confidence = min(0.95, max(0.6, len(response) / 500))
        
        return {
            "review": response,
            "analysis_type": "code_review",
            "model_used": model_id
        }, confidence
    
    def _analyze_requirements(self, content: str, model_id: str) -> Tuple[Dict[str, Any], float]:
        """Extract requirements from content."""
        prompt = f"Extract and list the key requirements from the following text:\n\n{content}"
        response = generate_response(prompt)
        
        # Use classification to determine content quality
        classifications = classify(content)
        confidence = 0.8 if classifications else 0.6
        
        return {
            "requirements": response,
            "classifications": classifications,
            "analysis_type": "requirement_extraction",
            "model_used": model_id
        }, confidence
    
    def _analyze_tech_recommendation(self, content: str, model_id: str) -> Tuple[Dict[str, Any], float]:
        """Generate technology recommendations."""
        prompt = f"Based on the following project description, recommend appropriate technologies and tools:\n\n{content}"
        response = generate_response(prompt)
        
        confidence = 0.75  # Medium confidence for tech recommendations
        
        return {
            "recommendations": response,
            "analysis_type": "tech_recommendation",
            "model_used": model_id
        }, confidence
    
    def _analyze_risk_assessment(self, content: str, model_id: str) -> Tuple[Dict[str, Any], float]:
        """Perform risk assessment."""
        prompt = f"Identify potential risks and mitigation strategies for the following:\n\n{content}"
        response = generate_response(prompt)
        
        confidence = 0.7  # Lower confidence for risk assessment as it requires domain expertise
        
        return {
            "risk_assessment": response,
            "analysis_type": "risk_assessment",
            "model_used": model_id
        }, confidence
    
    def _default_analysis(self, content: str, model_id: str) -> Tuple[Dict[str, Any], float]:
        """Perform default analysis."""
        response = generate_response(content)
        confidence = 0.8
        
        return {
            "generated_text": response,
            "analysis_type": "general",
            "model_used": model_id
        }, confidence
    
    def _generate_recommendations(self, results: dict, analysis_type: str) -> List[str]:
        """Generate actionable recommendations based on analysis results."""
        recommendations = []
        
        if analysis_type == "code_review":
            recommendations.extend([
                "Consider implementing automated testing",
                "Review code documentation",
                "Ensure proper error handling"
            ])
        elif analysis_type == "requirement_extraction":
            recommendations.extend([
                "Prioritize requirements by business value",
                "Validate requirements with stakeholders",
                "Consider technical feasibility"
            ])
        elif analysis_type == "tech_recommendation":
            recommendations.extend([
                "Evaluate team expertise with recommended technologies",
                "Consider scalability requirements",
                "Assess maintenance and support costs"
            ])
        elif analysis_type == "risk_assessment":
            recommendations.extend([
                "Develop contingency plans for high-risk items",
                "Regular risk assessment reviews",
                "Implement monitoring and alerting"
            ])
        
        return recommendations

    def check_hf_api_health(self):
        """Check HuggingFace API connectivity and health status.
        
        This method performs a lightweight health check on the HuggingFace API
        by making a simple request to verify connectivity and authentication.
        
        Returns:
            dict: Health status information containing:
                - status: 'healthy', 'degraded', or 'unhealthy'
                - message: Descriptive message about the API status
                - response_time_ms: API response time in milliseconds (if available)
                - last_error: Last error message (if any)
        """
        try:
            import time
            from scripts.ai_engine.model import _hf_request
            
            start_time = time.time()
            
            # Make a simple request to test API connectivity
            # Using a lightweight model call with minimal payload
            test_data = {"inputs": "test"}
            response = _hf_request("google/flan-t5-base", test_data, retries=1)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "status": "healthy",
                "message": "HuggingFace API is accessible and responding",
                "response_time_ms": response_time_ms
            }
            
        except ValueError as e:
            # This typically means API token is not set
            return {
                "status": "unhealthy",
                "message": "HuggingFace API configuration error",
                "last_error": str(e)
            }
        except Exception as e:
            # This could be network issues, API errors, etc.
            return {
                "status": "degraded",
                "message": "HuggingFace API connectivity issues",
                "last_error": str(e)
            }
    
    @lru_cache(maxsize=32)
    def get_available_models(self):
        """Get list of available models with caching."""
        return [
            {
                "id": model_id,
                "name": info["name"],
                "description": info["description"],
                "capabilities": info["capabilities"],
                "version": info["version"],
                "provider": info["provider"]
            }
            for model_id, info in self.supported_models.items()
        ]

