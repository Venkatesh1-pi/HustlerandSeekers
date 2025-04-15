import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    username = models.CharField(max_length=100, unique=True)
    email = models.CharField(max_length=100, null=True, blank=True)
    is_hustler = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to="users/images", null=True, blank=True)
    banner_image = models.ImageField(upload_to="users/banner", null=True, blank=True)
    dob = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    reset_code = models.CharField(max_length=255, null=True, blank=True)
    device_token = models.CharField(max_length=255, null=True, blank=True)
    radius_km = models.FloatField(default=25)  # 👈 New field added
    created_at = models.DateTimeField(auto_now_add=True)

