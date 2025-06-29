FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy necessary parent files
COPY ../../scripts/ai_engine/ ./scripts/ai_engine/
COPY ../../scripts/assistant/ai_engine/ ./scripts/assistant/ai_engine/

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Run the service
CMD ["./entrypoint.sh"]
