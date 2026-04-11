# Use an official lightweight Python image
FROM python:3.13-slim

# Set environment variables to ensure Python output is logged immediately
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (needed for some ML libraries)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn (Production-grade WSGI server)
RUN pip install gunicorn

# Copy the rest of the application code
COPY . .

# Create necessary directories for runtime
RUN mkdir -p logs models

# Expose the port Flask runs on
EXPOSE 5000

# Start the application using Gunicorn
# --workers 4: Handles multiple simultaneous requests
# --bind 0.0.0.0:5000: Makes the app accessible outside the container
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]