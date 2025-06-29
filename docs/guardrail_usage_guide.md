# Guardrail Usage Guide

This document outlines how to use the guardrail features in this project.

## Reviewing Agent PRs

When an agent submits a pull request, it will be accompanied by a summary of the automated guardrail checks that were performed. This summary will be included in the PR description. As a reviewer, it is your responsibility to:

1.  **Verify the Guardrail Summary:** Ensure the summary is present and that all checks have passed.
2.  **Inspect the Agent's Work:** The guardrails are a safety net, not a replacement for human review. Carefully examine the code changes for correctness, efficiency, and adherence to project standards.
3.  **Provide Feedback:** If you have any concerns, leave comments on the PR as you would for any other contribution.

## Piloting the Guardrail Suite

We are currently piloting the full guardrail suite on a small sample project. The goal of this pilot is to:

*   Collect metrics on the effectiveness of the guardrails.
*   Identify any areas where the guardrails are too restrictive or not restrictive enough.
*   Iterate on the guardrail implementation based on feedback from the pilot.

We will be collecting the following metrics:

*   Number of PRs submitted by agents.
*   Number of PRs that are automatically flagged by the guardrails.
*   Number of PRs that are approved after being flagged.
*   Number of PRs that are rejected after being flagged.

