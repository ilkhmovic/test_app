import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_app.settings')
django.setup()

print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD length: {len(settings.EMAIL_HOST_PASSWORD)}")
print(f"DEBUG: {settings.DEBUG}")
