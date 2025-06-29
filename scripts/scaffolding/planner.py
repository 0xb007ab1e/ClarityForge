
import json

def generate_plan(idea: str, stack: list[str]) -> dict:
    """
    Generates a project plan based on the project idea and technology stack.

    Args:
        idea: A description of the project idea.
        stack: A list of technologies to be used.

    Returns:
        A dictionary representing the project plan.
    """
    plan = {
        "project_name": "New Project",
        "epics": [
            {
                "name": "Core Functionality",
                "tasks": [
                    "Define data models",
                    "Implement business logic",
                    "Create API endpoints"
                ]
            },
            {
                "name": "User Management",
                "tasks": [
                    "Implement user authentication",
                    "Implement user authorization",
                    "Create user profile page"
                ]
            }
        ],
        "microservices": [
            "service-auth",
            "service-core"
        ],
        "stack": stack,
        "idea": idea
    }
    return plan

if __name__ == '__main__':
    project_idea = "A social media platform for sharing recipes."
    tech_stack = ["Python", "Flask", "PostgreSQL", "React"]
    project_plan = generate_plan(project_idea, tech_stack)
    print(json.dumps(project_plan, indent=4))

