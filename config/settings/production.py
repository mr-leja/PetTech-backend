from .base import *  # noqa

DEBUG = False

# Basic security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS enforcement (enable when the server has a valid SSL certificate)
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000          # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies transmitted only over HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
