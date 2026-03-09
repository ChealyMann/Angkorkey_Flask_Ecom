import os
from PIL import Image
from flask import current_app
from werkzeug.utils import secure_filename
import uuid


def save_picture(form_picture):
    random_hex = uuid.uuid4().hex
    filename = random_hex + ".webp"
    picture_path = os.path.join(current_app.root_path, 'static/images', filename)

    img = Image.open(form_picture)

    # Convert to RGB if it's RGBA to avoid transparency overhead (optional)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Fast WebP saving
    # method=0 or 1 is for speed. optimize=False is default but explicit here.
    img.save(picture_path, 'WEBP', quality=50, method=0, optimize=False)

    return filename