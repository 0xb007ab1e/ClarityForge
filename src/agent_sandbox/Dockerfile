# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Create a non-root user and group
RUN groupadd -r agent && useradd -r -g agent -m -d /home/agent agent

# Set the working directory in the container
WORKDIR /home/agent/app

# Copy the sandbox wrapper script
COPY sandbox_wrapper.sh /usr/local/bin/sandbox_wrapper.sh

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download the spacy model
RUN python -m spacy download en_core_web_md

# Copy the application code into the container
COPY . .

# Change the owner of the app directory
RUN chown -R agent:agent /home/agent/app

# Switch to the non-root user
USER agent

# Expose the port the app runs on
EXPOSE 8000

# Set the entrypoint to the sandbox wrapper
ENTRYPOINT ["/usr/local/bin/sandbox_wrapper.sh"]

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
