import typer

from assistant.conversation.main import run_conversation
from assistant.scaffolding.scaffolder import run_scaffolding

app = typer.Typer()

@app.command()
def start(
    skip_ai: bool = typer.Option(False, "--skip-ai", help="Skip AI conversation and run deterministic scaffolding."),
):
    """
    Starts the assistant.
    """
    if skip_ai:
        run_scaffolding()
    else:
        conversation_context = run_conversation()
        run_scaffolding(conversation_context)

if __name__ == "__main__":
    app()

