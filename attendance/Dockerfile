# Use official lightweight Python image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install only what we need
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project
COPY . .

# Create non-root user (security)
RUN adduser --disabled-password --gecos '' appuser
USER appuser

# Expose port
EXPOSE 8000

# Run the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]