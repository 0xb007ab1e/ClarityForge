
from scripts.assistant.ai_engine import AIEngine
from scripts.assistant.datastore import Datastore

class ConversationManager:
    def __init__(self, ai_engine: AIEngine, datastore: Datastore):
        self.ai_engine = ai_engine
        self.datastore = datastore
        self.conversation_history = []

    def start_conversation(self):
        """Starts and manages the conversation with the user."""
        initial_idea = self.prompt_for_initial_idea()
        self.conversation_history.append({"role": "user", "content": initial_idea})

        for _ in range(5):  # Loop for a maximum of 5 rounds
            question = self.ai_engine.generate_response(self.conversation_history)
            user_response = self.prompt_user(question)

            if user_response.lower() == "done":
                break
            
            # Check if user is requesting analysis
            if self._is_analysis_request(user_response):
                analysis_type = self._determine_analysis_type(user_response)
                analysis_result = self.analyze_conversation(analysis_type)
                self._display_analysis_results(analysis_result)
                
                # Ask if user wants to continue the conversation after analysis
                continue_response = input("Would you like to continue the conversation? (yes/no): ")
                if continue_response.lower() in ["no", "n"]:
                    break
            else:
                self.conversation_history.append({"role": "user", "content": user_response})

        distilled_idea = self.summarize_idea()
        self.datastore.save_idea(distilled_idea)
        print("Idea saved successfully!")

    def prompt_for_initial_idea(self) -> str:
        """Prompts the user for their initial idea."""
        return input("What is your initial idea? ")

    def prompt_user(self, question: str) -> str:
        """Prompts the user with a clarifying question."""
        return input(f"AI: {question}\nYou: ")

    def summarize_idea(self) -> str:
        """Summarizes the conversation to a distilled idea using enhanced AI analysis.
        
        This method now uses the AIEngine's analyze_and_summarize method for better
        summarization results while maintaining backward compatibility.
        """
        try:
            # Use enhanced summarization through analyze_content
            analysis_result = self.ai_engine.analyze_and_summarize(
                self.conversation_history, 
                analysis_type="summarization"
            )
            return analysis_result["summary"]
        except Exception as e:
            # Fallback to original method for backward compatibility
            print(f"Warning: Enhanced summarization failed ({str(e)}), using fallback method.")
            summarization_prompt = "Summarize the following conversation into a single, clear idea:"
            fallback_history = self.conversation_history + [{"role": "system", "content": summarization_prompt}]
            return self.ai_engine.generate_response(fallback_history)
    
    def analyze_conversation(self, analysis_type: str = "requirement_extraction") -> dict:
        """Perform detailed analysis of the conversation using AIEngine.
        
        Args:
            analysis_type: Type of analysis to perform (e.g., 'requirement_extraction', 
                         'tech_recommendation', 'risk_assessment')
        
        Returns:
            Dictionary containing analysis results including recommendations
        """
        try:
            return self.ai_engine.analyze_and_summarize(
                self.conversation_history,
                analysis_type=analysis_type
            )
        except Exception as e:
            return {
                "summary": f"Analysis failed: {str(e)}",
                "confidence": 0.0,
                "analysis_id": None,
                "recommendations": ["Please try again with valid input"],
                "processing_time_ms": 0,
                "full_results": {"error": str(e)}
            }
    
    def _is_analysis_request(self, user_input: str) -> bool:
        """Detect if user is requesting analysis of the conversation.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            True if the input appears to be requesting analysis
        """
        analysis_keywords = [
            "analyze", "analysis", "review", "summarize", "extract", "requirements",
            "recommend", "technology", "tech", "recommendation", "assess", "risk", "assessment",
            "what do you think", "feedback", "suggestions", "recommendations"
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in analysis_keywords)
    
    def _determine_analysis_type(self, user_input: str) -> str:
        """Determine the type of analysis requested by the user.
        
        Args:
            user_input: The user's input to analyze
            
        Returns:
            The analysis type to perform
        """
        user_input_lower = user_input.lower()
        
        if any(keyword in user_input_lower for keyword in ["requirements", "extract", "spec"]):
            return "requirement_extraction"
        elif any(keyword in user_input_lower for keyword in ["technology", "tech", "tools", "framework"]):
            return "tech_recommendation"
        elif any(keyword in user_input_lower for keyword in ["risk", "danger", "problem", "issue"]):
            return "risk_assessment"
        elif any(keyword in user_input_lower for keyword in ["code", "review", "quality"]):
            return "code_review"
        else:
            # Default to summarization for general analysis requests
            return "summarization"
    
    def _display_analysis_results(self, analysis_result: dict) -> None:
        """Display analysis results to the user in a formatted way.
        
        Args:
            analysis_result: The analysis results dictionary
        """
        print("\n" + "=" * 60)
        print("📊 CONVERSATION ANALYSIS RESULTS")
        print("=" * 60)
        
        # Display summary
        print(f"\n📝 Summary:")
        print(f"{analysis_result.get('summary', 'No summary available')}")
        
        # Display confidence and processing time
        confidence = analysis_result.get('confidence', 0.0)
        processing_time = analysis_result.get('processing_time_ms', 0)
        print(f"\n🎯 Confidence: {confidence:.2%}")
        print(f"⏱️  Processing Time: {processing_time}ms")
        
        # Display recommendations
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                print(f"   {i}. {rec}")
        
        # Display analysis ID for reference
        analysis_id = analysis_result.get('analysis_id')
        if analysis_id:
            print(f"\n🔍 Analysis ID: {analysis_id}")
            
        print("=" * 60 + "\n")


