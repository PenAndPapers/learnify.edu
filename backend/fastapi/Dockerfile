# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    python3-dev \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the pre-compiled requirements.txt directly from your host machine
COPY requirements.txt .

# Install the exact locked versions directly via standard pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your backend application code into /app
COPY . .

# Set Python path so the container can find your app/ module
ENV PYTHONPATH=/app

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]