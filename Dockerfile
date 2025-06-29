FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only=main --no-root
COPY . .
CMD ["poetry", "run", "python", "-m", "clarity_forge.cli", "serve", "--host", "0.0.0.0", "--port", "8000"]
