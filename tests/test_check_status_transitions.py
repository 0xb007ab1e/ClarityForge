import sys
sys.path.append('scripts')

import unittest
from unittest.mock import patch, MagicMock
from check_status_transitions import check_status_transitions

class TestCheckStatusTransitions(unittest.TestCase):

    @patch("subprocess.run")
    @patch("subprocess.check_output")
    def test_skipped_status(self, mock_check_output, mock_run):
        # Mock the output of the gh commands
        mock_check_output.side_effect = [
            b'{"timelineItems":[{"__typename":"AddedToProjectEvent","projectColumnName":"Backlog"},{"__typename":"AddedToProjectEvent","projectColumnName":"Done"}]}',
            b'{"columns":[{"name":"Backlog"},{"name":"To Do"},{"name":"In Progress"},{"name":"Done"}]}',
            b'{"labels":[]}'
        ]

        # Call the function with a dummy issue number and project id
        check_status_transitions("1", "1")

        # Verify that a comment was added to the issue
        mock_run.assert_called_with(["gh", "issue", "comment", "1", "--body", "Issue has skipped a required status. Expected order: ['Backlog', 'To Do', 'In Progress', 'Done']"])

if __name__ == "__main__":
    unittest.main(exit=False)
