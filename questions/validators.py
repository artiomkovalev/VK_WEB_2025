from django.core.exceptions import ValidationError

def validate_file_size(value):
    limit = 5 * 1024 * 1024
    if value.size > limit:
        raise ValidationError(f"File too large. Size should not exceed 5 MB")
