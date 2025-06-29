"""CLI entry point for ClarityForge."""

import json
import os
import subprocess

import click
import uvicorn


@click.group()
@click.version_option()
def cli():
    """ClarityForge - AI-powered development planning and architecture tool."""
    pass


@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
def serve(host: str = "0.0.0.0", port: int = 8000):
    """Run the API with uvicorn."""
    uvicorn.run("clarity_forge.api:app", host=host, port=port, reload=True)


@cli.command()
def setup():
    """Reuse scripts/setup_project.py logic."""

    # Import the setup functions from the existing script
    def create_labels(config):
        """Creates the standard issue labels for the project."""
        for label in config["issue_tracker"]["labels"]:
            subprocess.run(
                [
                    "gh",
                    "label",
                    "create",
                    label["name"],
                    "--color",
                    label["color"],
                    "--description",
                    label["description"],
                    "--force",
                ]
            )

    def seed_issues(config):
        """Seeds the issue tracker with the initial retrospective issues."""
        for issue in config["issue_tracker"]["seed_issues"]:
            subprocess.run(
                [
                    "gh",
                    "issue",
                    "create",
                    "--title",
                    issue["title"],
                    "--body",
                    issue["body"],
                    "--label",
                    ",".join(issue["labels"]),
                ]
            )

    def setup_project(config):
        """Sets up the project based on the configuration."""
        # Create directories
        for directory in config["project"]["directories"]:
            os.makedirs(directory, exist_ok=True)

        # Update README.md
        with open("README.md", "w") as f:
            f.write(f"# {config['project']['name']}\n\n")
            f.write(f"{config['project']['description']}\n")

    # Main setup logic
    try:
        with open("config/settings.json") as f:
            config = json.load(f)

        create_labels(config)
        seed_issues(config)
        setup_project(config)

        click.echo("Project setup complete!")
    except FileNotFoundError:
        click.echo(
            "Error: config/settings.json not found. Please ensure the configuration file exists."
        )
    except Exception as e:
        click.echo(f"Error during setup: {e}")


if __name__ == "__main__":
    cli()
