
import json
import os
import requests

# This is a placeholder for a more sophisticated model query
def query_model(prompt):
    """
    Queries a large language model with the given prompt.
    """
    # In a real implementation, this would make an API call to a model.
    # For this example, we'll return a hardcoded response.
    print(f"Querying model with prompt: {prompt}")
    return [
        {
            "name": "Python FastAPI + React + PostgreSQL",
            "pros": ["Fast development", "Great for APIs", "Scalable"],
            "cons": ["Requires separate frontend/backend teams"],
        },
        {
            "name": "Ruby on Rails + Hotwire",
            "pros": ["Convention over configuration", "Rapid development"],
            "cons": ["Can be slower than other frameworks"],
        },
        {
            "name": "Elixir Phoenix + LiveView",
            "pros": ["Excellent for real-time applications", "Highly concurrent"],
            "cons": ["Smaller community and ecosystem"],
        },
    ]

def search_duckduckgo(query):
    """
    Searches DuckDuckGo for the given query and returns the results as JSON.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "pretty": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

class TechStackRecommender:
    def __init__(self, datastore):
        self.datastore = datastore

    def recommend(self, distilled_idea, known_constraints):
        """
        Recommends a technology stack for the given idea and constraints.
        """
        prompt = f"Recommend 3 technology stacks for a project that is '{distilled_idea}' with the following constraints: {known_constraints}"
        recommendations = query_model(prompt)

        # Optional web enrichment
        for i, recommendation in enumerate(recommendations):
            search_query = f"trending web frameworks for {recommendation['name']}"
            search_results = search_duckduckgo(search_query)
            if search_results and "RelatedTopics" in search_results:
                trending_frameworks = [
                    topic["Text"] for topic in search_results["RelatedTopics"] if "Text" in topic
                ]
                recommendations[i]["trending"] = trending_frameworks

        while True:
            print("Here are some recommended technology stacks:")
            for i, recommendation in enumerate(recommendations):
                print(f"{i+1}. {recommendation['name']}")
                print(f"  Pros: {', '.join(recommendation['pros'])}")
                print(f"  Cons: {', '.join(recommendation['cons'])}")
                if "trending" in recommendation:
                    print(f"  Trending: {', '.join(recommendation['trending'])}")

            choice = input("Choose a stack (1-3) or type 'new' for a new set: ")
            if choice.isdigit() and 1 <= int(choice) <= 3:
                chosen_stack = recommendations[int(choice) - 1]
                self.datastore.save("chosen_stack", chosen_stack)
                print(f"You chose: {chosen_stack['name']}")
                return chosen_stack
            elif choice.lower() == "new":
                recommendations = query_model(prompt)
            else:
                print("Invalid choice. Please try again.")

if __name__ == '__main__':
    # This is a placeholder for a real datastore
    class Datastore:
        def __init__(self):
            self._data = {}

        def save(self, key, value):
            self._data[key] = value
            print(f"Saving {key} to datastore")

        def load(self, key):
            return self._data.get(key)

    datastore = Datastore()
    recommender = TechStackRecommender(datastore)
    recommender.recommend(
        "A social media platform for pet owners",
        ["Must be scalable to millions of users", "Needs a mobile app"],
    )

