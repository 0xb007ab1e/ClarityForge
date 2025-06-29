
import json
import logging
from datetime import datetime

from cryptography.fernet import Fernet

# Configure logging
logging.basicConfig(
    filename="data/conversation.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)


def log_interaction(role: str, text: str):
    """Logs a message to the conversation log."""
    logging.info(json.dumps({"role": role, "text": text}))


def store_project_state(idea: str, stack: str, plan: str):
    """Stores the project state in a JSON file."""
    state = {"idea": idea, "stack": stack, "plan": plan}
    with open("data/project_state.json", "w") as f:
        json.dump(state, f, indent=2)


def get_fernet_key() -> bytes:
    """
    Retrieves the Fernet encryption key from the environment or user input.
    """
    try:
        # Attempt to retrieve key from keyring
        import keyring

        key = keyring.get_password("your-app", "fernet-key")
        if key:
            return key.encode()
    except ImportError:
        pass  # Keyring not available

    # Fallback to .env file or user input
    try:
        from dotenv import load_dotenv
        import os

        load_dotenv()
        key = os.environ.get("FERNET_KEY")
        if key:
            return key.encode()
    except ImportError:
        pass  # Dotenv not available

    # If key is not found, prompt user for it
    key = input("Enter your Fernet encryption key: ")
    return key.encode()


def encrypt_secret(secret: str, key: bytes) -> bytes:
    """Encrypts a secret using the provided Fernet key."""
    f = Fernet(key)
    return f.encrypt(secret.encode())


def decrypt_secret(encrypted_secret: bytes, key: bytes) -> str:
    """Decrypts an encrypted secret using the provided Fernet key."""
    f = Fernet(key)
    return f.decrypt(encrypted_secret).decode()

