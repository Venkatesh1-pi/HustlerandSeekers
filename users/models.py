from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import base64
from django.db import models
from django.core.exceptions import ValidationError
from io import BytesIO
from PIL import Image as PILImage

class Base64ImageField(models.TextField):
    """
    Custom field to store image as base64 encoded data.
    """
    def to_python(self, value):
        if value:
            # Check if value is base64 encoded
            try:
                if isinstance(value, str):
                    # Strip any unwanted characters like 'data:image/png;base64,' if present
                    if value.startswith('data:image'):
                        value = value.split(',')[1]
                    return base64.b64decode(value)
                return value
            except Exception as e:
                raise ValidationError(f"Invalid base64 encoded data: {e}")
        return value

    def get_prep_value(self, value):
        if value:
            # Ensure the value is a valid base64 string before saving it
            try:
                if isinstance(value, bytes):
                    return base64.b64encode(value).decode('utf-8')
                return value
            except Exception as e:
                raise ValidationError(f"Unable to encode image to base64: {e}")
        return value

class Users(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    username = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    is_hustler = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    
    # Updated to base64 storage
    image = Base64ImageField(null=True, blank=True)
    banner_image = Base64ImageField(null=True, blank=True)
    
    dob = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    reset_code = models.CharField(max_length=255, null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    radius_km = models.FloatField(default=25)  # 👈 New field added
    created_at = models.DateTimeField(auto_now_add=True)
