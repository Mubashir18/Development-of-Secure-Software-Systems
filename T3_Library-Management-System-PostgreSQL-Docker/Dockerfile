FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir psycopg2-binary

# Copy application
COPY src/ /app/

# Create log directory
RUN mkdir -p /app/logs

# Set environment variables (can be overridden)
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=library_db
ENV DB_USER=postgres
ENV DB_PASSWORD=postgres
ENV LOG_FILE=/app/logs/app.log

CMD ["python", "main.py"]
