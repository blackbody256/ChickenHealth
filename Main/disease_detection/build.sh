aces/ChickenHealth/Main/disease_detection/build.sh
#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Starting build process..."

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Creating cache table..."
python manage.py createcachetable || echo "Cache table already exists"

echo "Build completed successfully!"