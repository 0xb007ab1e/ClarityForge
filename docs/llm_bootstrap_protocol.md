---
name: LLM Agent Project Bootstrap Protocol
about: A deterministic set of instructions for an LLM agent to initialize a new software project.
---
# LLM Agent Project Bootstrap Protocol

## Objective
This document provides a deterministic set of instructions for an LLM agent to initialize a new software project. By following this protocol, the agent will establish the project's identity, configure its development environment, define its own operational rules, and seed the initial project management backlog.

---

### **Directive: Project Identity Configuration**

1.  **Inquire & Establish Project Name:**
    *   **Initial Concepts:** `{List of initial name ideas}`
    *   **Final Selection:** `{ProjectName}`
    *   **Rationale:** `{Reason for choosing the final name}`

2.  **Define Project Vision:**
    *   **Vision Statement:** `{A clear, high-level statement describing the project's ultimate goal and impact.}`

---

### **Directive: Environment Configuration**

1.  **Version Control System (VCS) Setup:**
    *   **VCS Provider:** `{VCSProvider}` (e.g., GitHub, GitLab)
    *   **Repository Name:** Use the established `{ProjectName}`.
    *   **Visibility:** `Public`
    *   **Action:** Create a new remote repository and link the local project directory to it. Push the initial commit.

---

### **Directive: Agent Ruleset Configuration**

This is a mandatory, self-referential ruleset that the agent MUST adhere to for all subsequent actions.

1.  **Define Rule: Vision Alignment Check**
    *   **Trigger:** Before the creation of any new artifact (e.g., file, code, documentation).
    *   **Action:** Call the Vision Alignment service to compare the proposed artifact against the project's Vision Statement.
    *   **Guardrail:** If the service flags the artifact as a potential deviation, the agent MUST halt the current action and seek clarification from the user.

2.  **Define Rule: Ruleset Modification Documentation**
    *   **Trigger:** Any modification (creation, update, deletion) to the `Agent Ruleset`.
    *   **Action:** Create a new issue in the designated `{IssueTracker}`.
    *   **Issue Content:** The issue body MUST document the change, the rationale, and the user story for the modification.
    *   **Issue Labels:** `ruleset`, `process`, `documentation`

3.  **Define Rule: Continuous Commit Cadence**
    *   **Trigger:** The successful completion of any action that results in a file modification.
    *   **Action:** Add, commit, and push the resulting file(s) to the `{VCSProvider}`.
    *   **Commit Message Standard:** Adhere to the Conventional Commits specification (e.g., `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `test:`, `chore:`).

---

### **Directive: Project Management Configuration**

1.  **Issue Tracker Setup:**
    *   **Platform:** `{IssueTracker}` (e.g., GitHub Issues, Jira)
    *   **Action:** For the designated repository, define the following set of issue labels with descriptive text.
    *   **Label Definitions:**
        *   `planning`: Project management and high-level planning.
        *   `ruleset`: Related to the agent's operational rules.
        *   `documentation`: Tasks for writing or updating documentation.
        *   `retrospective`: Reviewing past actions and decisions.
        *   `process`: Defining or refining team and agent processes.
        *   `testing`: Quality assurance and testing tasks.
        *   `feature`: A new capability or enhancement.
        *   `bug`: An unexpected issue or error.

---

### **Directive: Backlog Seeding (Retrospective)**

Create the following issues in the `{IssueTracker}` to document the project's bootstrap process itself.

1.  **Seed Issue: Project Naming Retrospective**
    *   **Title:** `Retrospective: Project Naming Decision`
    *   **Body:** Document the brainstorming and selection process for `{ProjectName}`.
    *   **Labels:** `retrospective`, `documentation`

2.  **Seed Issue: Technical Setup Retrospective**
    *   **Title:** `Retrospective: Initial Technical Setup`
    *   **Body:** Document any challenges encountered during the initial environment setup, including command-line errors, tool misconfigurations, or other obstacles.
    *   **Labels:** `retrospective`, `testing`, `documentation`

3.  **Seed Issue: Process Definition**
    *   **Title:** `Process Definition: {ProjectName} Project Management`
    *   **Body:** Formally document the decision to use `{IssueTracker}` and the defined label taxonomy for managing the project.
    *   **Labels:** `process`, `documentation`

