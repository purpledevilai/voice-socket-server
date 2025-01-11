# Use Python 3.10 as the base image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies, including ffmpeg
RUN apt-get update && apt-get install -y \
    gcc \
    libasound2-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt to the working directory
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the src folder to the working directory
COPY src .

# Expose the WebSocket port
EXPOSE 8765

# Run the WebSocket server
CMD ["python", "./app.py"]
