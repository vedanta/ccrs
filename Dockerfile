FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create a non-root user
RUN useradd -m ccrs2 && chown -R ccrs2:ccrs2 /app
USER ccrs2

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["python", "app.py"]