import json
import os
import subprocess
import sys

def get_issue_events(issue_number):
    """Gets the event history for a given issue."""
    return subprocess.check_output([
        "gh", "issue", "view", issue_number, "--json", "timelineItems"
    ]).decode("utf-8")

def get_project_columns(project_id):
    """Gets the columns for a given project."""
    return subprocess.check_output([
        "gh", "project", "view", project_id, "--json", "columns"
    ]).decode("utf-8")

def check_status_transitions(issue_number, project_id):
    """Checks if the issue has moved through the required stati."""
    events = json.loads(get_issue_events(issue_number))["timelineItems"]
    columns = json.loads(get_project_columns(project_id))["columns"]

    required_stati = [col["name"] for col in columns]
    actual_stati = []

    for event in events:
        if event["__typename"] == "AddedToProjectEvent":
            actual_stati.append(event["projectColumnName"])

    is_hotfix = "hotfix" in [label["name"] for label in json.loads(subprocess.check_output(["gh", "issue", "view", issue_number, "--json", "labels"]))["labels"]]

    if is_hotfix and actual_stati[-1] == "Done":
        return

    if len(actual_stati) < len(required_stati) -1 and not is_hotfix:
        subprocess.run([
            "gh", "issue", "comment", issue_number, "--body",
            f"Issue has skipped a required status. Expected order: {required_stati}"
        ])

def main():
    """Reads the list of issues and checks their status transitions."""
    project_id = subprocess.check_output(["gh", "project", "list", "--owner", "@me", "--json", "id", "--jq", ".[0].id"]).decode("utf-8").strip()

    issues = json.loads(subprocess.check_output(["gh", "issue", "list", "--json", "number"])) 
    for issue in issues:
        check_status_transitions(str(issue['number']), project_id)

if __name__ == "__main__":
    main()
