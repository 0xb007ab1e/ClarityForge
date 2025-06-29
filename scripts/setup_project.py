#!/usr/bin/env python3
"""DEPRECATED: Project setup script.

This script is deprecated. Please use the clarity_forge.core.project_setup module instead.

For CLI usage:
    python -m clarity_forge.core.project_setup

For programmatic usage:
    from clarity_forge.core.project_setup import setup_project_from_config
    setup_project_from_config()
"""

import argparse
import warnings
from clarity_forge.core.project_setup import setup_project_from_config

def main():
    """Main entry point - DEPRECATED."""
    warnings.warn(
        "Direct execution of scripts/setup_project.py is deprecated. "
        "Use 'from clarity_forge.core.project_setup import setup_project_from_config' instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    print("[DEPRECATED] This script is deprecated. Using new library code...")
    setup_project_from_config()
    print("Project setup complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Setup the project.')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode.')
    args = parser.parse_args()

    if args.interactive:
        from assistant.main import start
        start()
    else:
        main()
