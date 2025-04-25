from django.db import models

import base64
from django.db import models
from django.core.exceptions import ValidationError

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
from django.db import models
from django.core.exceptions import ValidationError
import base64

class Base64VideoField(models.TextField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        if isinstance(value, str):
            if value.startswith('data:'):
                try:
                    # Check if it's a valid base64-encoded video
                    header, encoded = value.split(';base64,')
                    file_type = header.split(':')[1]
                    
                    # Validate the MIME type, ensure it's a video
                    if not file_type.startswith('video'):
                        raise ValidationError("Invalid video format. Only video files are allowed.")
                    
                    # If it's a valid base64 video string, return the value
                    return value
                except Exception as e:
                    raise ValidationError(f"Invalid base64 video data: {str(e)}")
        
        # If it's not a base64 string, return it as is
        return super().clean(value, model_instance)

class UsersCategory(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.CharField(max_length=100, null=True, blank=True)
    role_category_name = models.CharField(max_length=100, null=True, blank=True)
    summary = models.CharField(max_length=500, null=True, blank=True)
    about_yourself = models.CharField(max_length=500, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.CharField(max_length=255, null=True, blank=True)
    longitude = models.CharField(max_length=255, null=True, blank=True)
    image1 = Base64ImageField(null=True, blank=True)
    image2 = Base64ImageField(null=True, blank=True)
    image3 = Base64ImageField(null=True, blank=True)
    video =  Base64VideoField(null=True, blank=True)

    twitter_link = models.CharField(max_length=255, null=True, blank=True)
    isnta_link = models.CharField(max_length=255, null=True, blank=True)
    fb_link = models.CharField(max_length=255, null=True, blank=True)
    linkedin_link = models.CharField(max_length=255, null=True, blank=True)
    yt_link = models.CharField(max_length=255, null=True, blank=True)
    other_link = models.CharField(max_length=255, null=True, blank=True)

    IS_PRIMARY_CHOICES = (
        (0, 'No'),
        (1, 'Yes'),
    )

    is_primary = models.IntegerField(choices=IS_PRIMARY_CHOICES, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.role_category_name}"


class UsersPosts(models.Model):

	user_id=models.CharField(max_length=100, null=True, blank=True)
	summary=models.CharField(max_length=500, null=True, blank=True)
	video=models.FileField(upload_to="users/posts/", null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

class Chat(models.Model):

	category_id=models.CharField(max_length=100, null=True, blank=True)
	category_name=models.CharField(max_length=100, null=True, blank=True)
	sender_id=models.CharField(max_length=100, null=True, blank=True)
	receiver_id=models.CharField(max_length=100, null=True, blank=True)
	message=models.CharField(max_length=500, null=True, blank=True)
	status=models.CharField(max_length=500, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
