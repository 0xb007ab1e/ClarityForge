import os
import subprocess
import pytest


def test_forbidden_command():
    """Verify that forbidden commands are blocked by the sandbox."""
    with pytest.raises(subprocess.CalledProcessError) as e:
        subprocess.run(["/bin/sh", "-c", "ls"], check=True, capture_output=True)
    assert "Command not allowed" in e.value.stderr.decode()

def test_filesystem_access():
    """Verify that the agent can only access the allowed directory."""
    # This test assumes that the agent is running inside the container
    # and the working directory is /home/agent/app
    assert os.getcwd() == "/home/agent/app"

    # The agent should be able to access files in its working directory
    with open("main.py", "r") as f:
        content = f.read()
    assert content is not None

    # The agent should not be able to access files outside its working directory
    with pytest.raises(FileNotFoundError):
        with open("/etc/passwd", "r") as f:
            f.read()
