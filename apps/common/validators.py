from django.core.exceptions import ValidationError
from PIL import Image, UnidentifiedImageError

MAX_IMAGE_SIZE_BYTES = 4 * 1024 * 1024  # 4 MB
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


def validate_image_file(file):
    if file.size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"Image must be smaller than {MAX_IMAGE_SIZE_BYTES // (1024 * 1024)} MB.")

    try:
        image = Image.open(file)
        image.verify()
    except (UnidentifiedImageError, OSError):
        raise ValidationError("This file is not a valid image.")

    if image.format not in ALLOWED_IMAGE_FORMATS:
        raise ValidationError("Only JPEG, PNG, and WEBP images are allowed.")

    # verify() moves the pointer
    file.seek(0)
