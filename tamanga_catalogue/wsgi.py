"""
WSGI config for tamanga_catalogue project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tamanga_catalogue.settings')

application = get_wsgi_application()
application = WhiteNoise(application, root='staticfiles')
application.add_files('build')