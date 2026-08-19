# Dockerfile for CodeGuard AI Enterprise

# Base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/
COPY assets/ /app/assets/

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000
EXPOSE 8501

# Copy a startup script
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# Command to run both services
CMD ["/app/start.sh"]
