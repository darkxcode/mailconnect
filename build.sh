#!/usr/bin/env bash
# exit on error
set -o errexit

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create logs directory
mkdir -p logs
chmod 777 logs

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Check if superuser exists, if not create it
if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(username='admin').exists())"; then
    python manage.py createsuperuser --noinput --username admin --email admin@mailconnect.com
fi 