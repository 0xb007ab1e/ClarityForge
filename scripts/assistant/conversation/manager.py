
from assistant.ai_engine import AIEngine
from assistant.datastore import Datastore

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
        """Summarizes the conversation to a distilled idea."""
        # Use a specific summarization instruction or head if available
        summarization_prompt = "Summarize the following conversation into a single, clear idea:"
        self.conversation_history.append({"role": "system", "content": summarization_prompt})
        summary = self.ai_engine.generate_response(self.conversation_history)
        return summary


