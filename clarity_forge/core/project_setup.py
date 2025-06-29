"""Project setup functionality for ClarityForge.

This module provides functions to set up a project including creating labels,
seeding issues, and setting up the project structure.

Example CLI usage:
    python -m clarity_forge.core --config config/settings.json
    python -m clarity_forge.core --dry-run --config config/settings.json

Example programmatic usage:
    from clarity_forge.core.project_setup import (
        setup_project_from_config, CommandRunner, create_labels
    )

    # Basic usage
    setup_project_from_config('config/settings.json')

    # With custom command runner (e.g., for testing)
    runner = CommandRunner(dry_run=True)
    setup_project_from_config('config/settings.json', runner)

    # Individual functions
    with open('config/settings.json') as f:
        config = json.load(f)
    create_labels(config, runner=runner)
"""

import json
import os
import subprocess
from typing import Any


class CommandRunner:
    """Thin wrapper around subprocess.run for command execution.

    This allows both CLI and API consumers to customize command execution
    behavior (e.g., for testing, logging, or different execution contexts).
    """

    def __init__(self, dry_run: bool = False, capture_output: bool = False):
        """Initialize the command runner.

        Args:
            dry_run: If True, commands will be logged but not executed
            capture_output: If True, capture and return command output
        """
        self.dry_run = dry_run
        self.capture_output = capture_output

    def run(self, command: list[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command with optional dry-run mode.

        Args:
            command: List of command arguments
            **kwargs: Additional arguments passed to subprocess.run

        Returns:
            CompletedProcess instance
        """
        if self.dry_run:
            print(f"[DRY RUN] Would execute: {' '.join(command)}")
            # Return a mock CompletedProcess for dry runs
            return subprocess.CompletedProcess(
                args=command,
                returncode=0,
                stdout=b"" if self.capture_output else None,
                stderr=b"" if self.capture_output else None,
            )

        # Set default capture_output if specified in runner
        if self.capture_output and "capture_output" not in kwargs:
            kwargs["capture_output"] = True

        return subprocess.run(command, **kwargs)


def create_labels(config: dict[str, Any], runner: CommandRunner | None = None) -> None:
    """Creates the standard issue labels for the project.

    Args:
        config: Project configuration dictionary
        runner: Command runner instance (uses default if None)
    """
    if runner is None:
        runner = CommandRunner()

    for label in config["issue_tracker"]["labels"]:
        runner.run(
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


def seed_issues(config: dict[str, Any], runner: CommandRunner | None = None) -> None:
    """Seeds the issue tracker with the initial retrospective issues.

    Args:
        config: Project configuration dictionary
        runner: Command runner instance (uses default if None)
    """
    if runner is None:
        runner = CommandRunner()

    for issue in config["issue_tracker"]["seed_issues"]:
        runner.run(
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


def setup_project(config: dict[str, Any], runner: CommandRunner | None = None) -> None:
    """Sets up the project based on the configuration.

    Args:
        config: Project configuration dictionary
        runner: Command runner instance (uses default if None)
    """
    if runner is None:
        runner = CommandRunner()

    # Create directories
    for directory in config["project"]["directories"]:
        os.makedirs(directory, exist_ok=True)

    # Update README.md
    with open("README.md", "w") as f:
        f.write(f"# {config['project']['name']}\n\n")
        f.write(f"{config['project']['description']}\n")


def setup_project_from_config(
    config_path: str = "config/settings.json", runner: CommandRunner | None = None
) -> None:
    """Complete project setup from configuration file.

    Args:
        config_path: Path to the configuration JSON file
        runner: Command runner instance (uses default if None)
    """
    with open(config_path) as f:
        config = json.load(f)

    create_labels(config, runner)
    seed_issues(config, runner)
    setup_project(config, runner)
