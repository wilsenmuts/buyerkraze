import os
from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

MAX_DIMENSION = 1600
WEBP_QUALITY = 80


def optimize_image_field(field_file):
    """Resize to MAX_DIMENSION and re-encode as WebP. No-op for already-saved files."""
    if not field_file or getattr(field_file, '_committed', True):
        return
    try:
        field_file.file.seek(0)
        img = ImageOps.exif_transpose(Image.open(field_file.file))
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)
        has_alpha = img.mode in ('RGBA', 'LA', 'P')
        img = img.convert('RGBA' if has_alpha else 'RGB')
        buf = BytesIO()
        img.save(buf, format='WEBP', quality=WEBP_QUALITY, method=6)
    except Exception:
        return  # keep the original upload if it can't be processed
    base = os.path.splitext(os.path.basename(field_file.name))[0]
    field_file.save(f'{base}.webp', ContentFile(buf.getvalue()), save=False)
