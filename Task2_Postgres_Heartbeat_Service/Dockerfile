# Use Python base image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all files
COPY . .

# Default command (unbuffered output for real-time logs)
CMD ["python", "-u", "pinger.py"]