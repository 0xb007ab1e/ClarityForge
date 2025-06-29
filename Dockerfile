FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev
COPY . .
CMD ["clarity-forge", "serve", "--host", "0.0.0.0", "--port", "8000"]
