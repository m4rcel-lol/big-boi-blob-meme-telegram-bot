# Use official Python runtime as base image
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the bot code and memes
COPY bot.py .
COPY memes/ ./memes/

# Run the bot
CMD ["python", "bot.py"]
