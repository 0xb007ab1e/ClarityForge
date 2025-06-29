#!/usr/bin/env python3
"""CLI entry point for clarity_forge.core.project_setup module."""

import argparse

from .project_setup import CommandRunner, setup_project_from_config


def main():
    """Main CLI entry point for project setup."""
    parser = argparse.ArgumentParser(
        description="Setup a ClarityForge project from configuration.",
        prog="python -m clarity_forge.core",
    )
    parser.add_argument(
        "--config",
        "-c",
        default="config/settings.json",
        help="Path to configuration file (default: config/settings.json)",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Show what commands would be run without executing them",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Create command runner with appropriate options
    runner = CommandRunner(dry_run=args.dry_run, capture_output=args.verbose)

    try:
        print(f"Setting up project from config: {args.config}")
        if args.dry_run:
            print("[DRY RUN MODE] No commands will be executed")

        setup_project_from_config(args.config, runner)

        if not args.dry_run:
            print("Project setup complete!")
        else:
            print("Dry run complete!")

    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {e}")
        return 1
    except Exception as e:
        print(f"Error during project setup: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
