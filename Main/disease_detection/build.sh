#!/usr/bin/env bash
set -o errexit

echo "🔄 Starting build process..."

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

echo "📁 Preparing static files structure..."
# Create static media directory if it doesn't exist
mkdir -p static/media/

# Copy logo file to static directory if it exists in parent directory
if [ -f "../betterkukulogo.jpg" ]; then
    echo "📸 Copying logo file to static directory..."
    cp ../betterkukulogo.jpg static/media/betterkukulogo.jpg
fi

# Create a fallback logo if the original doesn't exist
if [ ! -f "static/media/betterkukulogo.jpg" ]; then
    echo "⚠️ Logo file not found, creating placeholder..."
    # You can add a default image or create an empty file
    touch static/media/betterkukulogo.jpg
fi

echo "🎨 Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "🗄️ Running database migrations..."
python manage.py migrate

echo "💾 Creating cache table..."
python manage.py createcachetable || echo "Cache table already exists"

echo "🔍 Verifying static files..."
python -c "
import os
from django.conf import settings
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'disease_detection.settings')
django.setup()

from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.staticfiles import finders

# Check if logo exists
try:
    logo_path = staticfiles_storage.url('media/betterkukulogo.jpg')
    print('✅ Logo file found in static storage')
except:
    print('❌ Logo file missing from static storage')
    
# List some static files for debugging
print('📂 Static files found:')
for finder in finders.get_finders():
    for path, storage in finder.list([]):
        if 'media' in path:
            print(f'  {path}')
"

echo "✅ Build completed successfully!"