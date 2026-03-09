import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

# Caching Configuration
CACHE_TYPE = "SimpleCache"
CACHE_DEFAULT_TIMEOUT = 300
SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year (static asset caching)

# Rate Limiting Configuration
RATELIMIT_DEFAULT = "60 per minute"

