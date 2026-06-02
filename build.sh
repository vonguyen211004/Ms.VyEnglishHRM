#!/bin/bash
set -o errexit

echo "Installing dependencies..."
pip install -r hr_management/requirements.txt

echo "Running migrations..."
cd hr_management
python manage.py migrate

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Setup complete!"
