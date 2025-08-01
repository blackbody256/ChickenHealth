FROM nvidia/cuda:11.4.3-base-ubuntu20.04

# Install Python and other dependencies
RUN apt-get update && apt-get install -y \
    python3.7 \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pip for python3.7
RUN curl https://bootstrap.pypa.io/get-pip.py | /usr/bin/python3.7

# Set Python 3.7 as the default
RUN ln -s /usr/bin/python3.7 /usr/bin/python

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY Main/disease_detection/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set work directory to the Django project
WORKDIR /app/Main/disease_detection

# Download the model from Google Cloud Storage
RUN curl -L "https://storage.googleapis.com/chicken-health-app-storage/efficientnetb3-Chicken%20Disease-98.27.h5" -o model.h5

# Create necessary directories
RUN mkdir -p static/media/ staticfiles/ media/

# Collect static files
RUN python manage.py collectstatic --noinput --settings=disease_detection.settings

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run the application
CMD exec gunicorn disease_detection.wsgi:application     --bind 0.0.0.0:$PORT     --workers 9     --worker-class gevent     --timeout 600     --max-requests 1000     --max-requests-jitter 100     --preload     --access-logfile -     --error-logfile -