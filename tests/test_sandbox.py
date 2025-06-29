import os
import subprocess
import pytest


import tempfile

import tempfile

def test_forbidden_command():
    """Verify that forbidden commands are blocked by the sandbox."""
    with pytest.raises(subprocess.CalledProcessError) as e:
        subprocess.run(["src/agent_sandbox/sandbox_wrapper.sh", "ls"], check=True, capture_output=True)
    assert b"Command not allowed" in e.value.stderr

def test_filesystem_access():
    """Verify that the agent can only access the allowed directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # The agent should be able to access files in its working directory
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")

        with open(os.path.join(tmpdir, "test.txt"), "r") as f:
            content = f.read()
        assert content == "test"

        # The agent should not be able to access files outside its working directory
        with pytest.raises(subprocess.CalledProcessError) as e:
            subprocess.run(["src/agent_sandbox/sandbox_wrapper.sh", "cat", "/etc/passwd"], check=True, capture_output=True)
        assert b"Command not allowed" in e.value.stderr
