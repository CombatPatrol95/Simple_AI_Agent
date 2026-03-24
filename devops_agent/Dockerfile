FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for CLI tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy agent source code
COPY . .

# Expose port for ADK web UI
EXPOSE 8000

# Default: run the ADK Developer UI
CMD ["adk", "web", "devops_agent"]
