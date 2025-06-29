
import os

def create_service_folders(service_name: str):
    """
    Creates service folders with an IoC pattern.

    Args:
        service_name: The name of the service.
    """
    base_dir = os.path.join("src", service_name)
    interfaces_dir = os.path.join(base_dir, "interfaces")
    os.makedirs(interfaces_dir, exist_ok=True)
    with open(os.path.join(base_dir, "__init__.py"), "w") as f:
        f.write("# I am a service module")

def create_project_documentation():
    """
    Produces README.md and ARCHITECTURE.md.
    """
    with open("README.md", "w") as f:
        f.write("# Project README")
    with open("ARCHITECTURE.md", "w") as f:
        f.write("# Project Architecture")

def create_starter_configs():
    """
    Produces starter configs for Docker and CI.
    """
    # In a real scenario, these would be templates
    with open("Dockerfile", "w") as f:
        f.write("FROM python:3.9-slim")
    with open(".github/workflows/ci.yml", "w") as f:
        f.write("name: CI")

if __name__ == '__main__':
    # Example usage:
    create_service_folders("my-awesome-service")
    create_project_documentation()
    create_starter_configs()
    print("Project scaffolding complete!")

