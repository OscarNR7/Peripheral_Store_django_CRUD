"""
Settings package initialization.
Default to using local settings for development.
Production settings are used when IS_RENDER or DJANGO_SETTINGS_MODULE=crud_ecommerce.settings.production.
"""

import os

if os.environ.get('IS_RENDER', 'False') == 'True':
    from .production import *
else:
    try:
        from .local import *
    except ImportError:
        from .base import *