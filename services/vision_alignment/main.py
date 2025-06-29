from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy

app = FastAPI()

# Load a pre-trained NLP model
nlp = spacy.load("en_core_web_md")

# Store the Vision Statement
vision_statement = """
The LLM Agent project aims to create a system that can autonomously bootstrap a software project from a set of high-level requirements.
This includes setting up the development environment, configuring version control, and seeding the project backlog with initial tasks.
The agent should be able to interact with various tools and services, such as Git, GitHub, and issue trackers.
The ultimate goal is to accelerate the initial phase of software development and reduce the manual effort required to start a new project.
"""
vision_vector = nlp(vision_statement)

class Artifact(BaseModel):
    content: str

@app.post("/check_alignment/")
async def check_alignment(artifact: Artifact):
    """
    Compares the artifact against the vision statement and returns a similarity score.
    A score below 0.85 will be flagged as a potential deviation.
    """
    artifact_vector = nlp(artifact.content)
    similarity = vision_vector.similarity(artifact_vector)

    if similarity < 0.85:
        return {"status": "FLAGGED", "similarity": similarity}
    else:
        return {"status": "OK", "similarity": similarity}
