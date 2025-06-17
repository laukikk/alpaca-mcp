# Base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements file
COPY . .

# Install dependencies
RUN uv venv .venv \
 && . .venv/bin/activate \
 && uv pip install --no-cache-dir -e .

# Expose port
EXPOSE 8000

# Set environment variables
ENV APP_NAME="alpaca-mcp-server"

# Command to run the application
CMD ["python", "server.py"]
