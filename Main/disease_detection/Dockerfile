FROM python:3.7.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set Google Drive model ID as a build argument
ARG MODEL_GDRIVE_ID
# Download the model from Google Drive
RUN pip install gdown && gdown --id ${MODEL_GDRIVE_ID}

# Copy project
COPY . .

# Create static files directory
RUN mkdir -p static/media/

# Copy logo if exists or create placeholder
RUN if [ -f "../betterkukulogo.jpg" ]; then \
        cp ../betterkukulogo.jpg static/media/betterkukulogo.jpg; \
    else \
        echo "KukuIntel Logo" > static/media/betterkukulogo.jpg; \
    fi

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8080

# Run the application
CMD exec gunicorn disease_detection.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 300 \
    --max-requests 1000 \
    --preload