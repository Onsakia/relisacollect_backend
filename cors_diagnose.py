#!/usr/bin/env python
import os, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_collect.settings')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import django
django.setup()
from django.conf import settings

print("=" * 60)
print("CORS DIAGNOSTIC")
print("=" * 60)

print("\n[1] corsheaders installed?")
try:
    import corsheaders
    print("  OK")
except ImportError:
    print("  FAIL - pip install django-cors-headers")

print("\n[2] Middleware (CorsMiddleware must be first):")
for i, mw in enumerate(settings.MIDDLEWARE):
    print(f"  {i+1}. {mw}{' <<< CORS' if 'CorsMiddleware' in mw else ''}")

print("\n[3] ALLOWED_HOSTS:")
print(f"  {settings.ALLOWED_HOSTS}")
if settings.ALLOWED_HOSTS == [] or settings.ALLOWED_HOSTS == ['']:
    print("  FAIL - EMPTY! Remove 'ALLOWED_HOSTS = []' line from settings.py")

print("\n[4] CORS_ALLOW_ALL_ORIGINS:")
print(f"  {getattr(settings, 'CORS_ALLOW_ALL_ORIGINS', 'NOT SET')}")

print("\n[5] CORS_ALLOWED_ORIGINS:")
print(f"  {getattr(settings, 'CORS_ALLOWED_ORIGINS', 'NOT SET')}")

print("\n[6] INSTALLED_APPS check:")
for app in ['corsheaders', 'rest_framework', 'collect']:
    print(f"  {'OK' if app in settings.INSTALLED_APPS else 'FAIL'} {app}")

print("\n" + "=" * 60)
