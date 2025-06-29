---
name: Project Bootstrap & Documentation Template
about: A structured process for initiating a new project, from idea to initial backlog.
---
# Project Bootstrap & Documentation Template

This template provides a structured process for initiating a new project, from idea to initial backlog. It is designed to be technology and platform agnostic.

---

## Phase 1: Project Initiation & Naming

The goal of this phase is to establish a clear identity and high-level vision for the project.

### Step 1.1: Brainstorm & Select a Project Name

Document the process of choosing a name for your project. This helps preserve the context behind the branding.

*   **Brainstorming Notes:**
    *   *Initial Idea 1*
    *   *Initial Idea 2*
    *   *Initial Idea 3*
*   **Final Selection:** `{ProjectName}`
*   **Rationale:** *Explain why this name was chosen. Does it align with a mission, a metaphor, or a companion product?*

### Step 1.2: Define High-Level Goals

State the project's mission and vision. What problem is it trying to solve?

*   **Project Vision:** *Describe the long-term impact you hope to achieve.*
*   **Mission Statement:** *Provide a one-sentence summary of the project's core purpose.*

---

## Phase 2: Technical Setup & Scoping

This phase focuses on setting up the foundational technical infrastructure and documenting initial explorations.

### Step 2.1: Create & Link Version Control Repository

All code and documentation should be stored in a version control system.

1.  Create a new repository on your chosen `{VCSProvider}` (e.g., GitHub, GitLab, Bitbucket).
2.  Link your local project directory to the remote repository.
    ```bash
    git init
    git remote add origin {RepoURL}
    git add .
    git commit -m "Initial commit"
    git push -u origin main
    ```

### Step 2.2: Document Initial Technical Exploration (Retrospective)

It's common to encounter challenges and learn valuable lessons during initial setup. Documenting them is crucial for future development.

**Create a retrospective ticket in your `{IssueTracker}` with the following format:**

*   **Title:** `Retrospective: Initial Technical Exploration on {TechnologyStack}`
*   **Body:**
    *   **Summary:** *Describe the initial technical tasks you attempted (e.g., setting up a database, testing a framework).*
    *   **Challenges:** *What obstacles did you encounter? (e.g., configuration issues, dependency conflicts, unexpected errors).*
    *   **Actionable Insights:** *What did you learn? What would you do differently next time? What improvements could be made to the process or tooling?*
*   **Labels/Topics:** `retrospective`, `technical-debt`, `documentation`

---

## Phase 3: Process Definition & Implementation

A clear and consistent project management process is key to success.

### Step 3.1: Define Project Management Process

Choose and configure your issue tracking system.

1.  Select your `{IssueTracker}` (e.g., GitHub Issues, Jira, Asana).
2.  Configure the project board, workflows, and integrations.

### Step 3.2: Create Issue Labels/Categories

A good labeling system helps to organize and prioritize work. Create a set of initial labels.

*   **`bug`**: An unexpected issue or error.
*   **`feature`**: A new capability or enhancement.
*   **`documentation`**: Tasks related to writing documentation.
*   **`planning`**: High-level project management and planning tasks.
*   **`testing`**: Tasks related to quality assurance.
*   **`retrospective`**: Reviewing past work to identify improvements.
*   **`process`**: Tasks related to defining and refining team processes.

### Step 3.3: Document the Process

Create an issue or a wiki page to formally document the chosen project management process.

*   **Title:** `Process Definition: {ProjectName} Project Management`
*   **Body:** *Outline the workflow (e.g., "To Do -> In Progress -> In Review -> Done"), the purpose of each label, and any other relevant guidelines for the team.*
*   **Labels/Topics:** `process`, `documentation`

---

## Phase 4: Initial Backlog Creation

Populate your issue tracker with the initial set of tasks to get the project moving.

### Step 4.1: Document Key Decisions

Create issues to document all major decisions made so far. This creates a transparent audit trail.

*   *Example: Create an issue for the project naming decision.*
*   *Example: Create an issue for the choice of `{TechnologyStack}`.*

### Step 4.2: Create Initial Feature Stories

Define the first few features to be built using a user story format.

**Create a feature ticket in your `{IssueTracker}` for each initial feature:**

*   **Title:** `Feature: {Feature Name}`
*   **Body:**
    *   **User Story:** As a `{UserRole}`, I want to `{Action}` so that I can `{Benefit}`.
    *   **Acceptance Criteria:**
        *   *Criterion 1*
        *   *Criterion 2*
    *   **Definition of Done:**
        *   *Code is peer-reviewed.*
        *   *Unit tests are written and passing.*
        *   *Documentation is updated.*
*   **Labels/Topics:** `feature`

