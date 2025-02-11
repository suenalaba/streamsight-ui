FROM python:3.12.5-slim

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set the working directory
WORKDIR /app

# Copy only the necessary files
COPY src /app/src
COPY pyproject.toml /app/pyproject.toml
COPY .python-version /app/.python-version
COPY uv.lock /app/uv.lock

# Install the application dependencies.
# WORKDIR /app
RUN uv sync --frozen --no-cache

EXPOSE 80

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "src/main.py", "--port", "80", "--host", "0.0.0.0"]