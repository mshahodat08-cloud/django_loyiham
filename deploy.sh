#!/bin/bash

echo "🚀 Deploy boshlandi..."

cd /var/www/django_loyiham

git pull origin main

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate --noinput
python manage.py collectstatic --noinput

sudo systemctl restart gunicorn
sudo systemctl restart nginx

echo "✅ Deploy tugadi!"
