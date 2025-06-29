# Agent Ruleset

This file contains the core ruleset for the agent.

## Rules

*   Store `Agent Ruleset` in a signed, version-pinned file.
*   CI refuses merges if core rules are altered without a **“ruleset change”** issue plus an approved review from a human maintainer.

## Immutability and Change Workflow

This file is signed and version-pinned. Any changes to the core ruleset must be accompanied by a "ruleset change" issue and an approved review from a human maintainer. This is enforced by the CI/CD pipeline.
