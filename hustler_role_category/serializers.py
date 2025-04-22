# users/serializers.py

from rest_framework import serializers
from .models import UsersCategory
from django.db import IntegrityError

import base64
from rest_framework import serializers
from .models import UsersCategory

class UsersCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersCategory
        fields = [
            'user_id', 'role_category_name',  'is_primary'
        ]

    def create(self, validated_data):
        # Clean base64 if it contains data headers
        def clean_base64(data):
            if data and isinstance(data, str) and data.startswith("data:"):
                return data.split(",")[1]
            return data

        category = UsersCategory.objects.create(
            user_id=validated_data.get('user_id'),
            role_category_name=validated_data.get('role_category_name'),
          
            is_primary=validated_data.get('is_primary'),
        )
        return category


import base64
from rest_framework import serializers
from .models import UsersCategory  # adjust this import to your app structure

import base64

class UpdateUsersCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersCategory
        fields = [
            'id', 'user_id', 'about_yourself',
            'image1', 'image2', 'image3', 'video', 'is_primary'
        ]

    def update(self, instance, validated_data):
        # Update 'about_yourself'
        instance.about_yourself = validated_data.get('about_yourself', instance.about_yourself)

        # Decode and update base64 images (image1, image2, image3)
        for field in ['image1', 'image2', 'image3']:
            image_data = validated_data.get(field, None)
            if image_data:
                if image_data.startswith("data:image"):
                    image_data = image_data.split(",")[1]
                instance.field = base64.b64encode(base64.b64decode(image_data)).decode('utf-8')

        # Decode and update base64 video
        video_data = validated_data.get('video', None)
        if video_data:
            if video_data.startswith("data:video"):
                video_data = video_data.split(",")[1]  # Remove the base64 prefix
            # Store the base64-encoded video directly (no need to re-encode)
            instance.video = base64.b64encode(base64.b64decode(video_data)).decode('utf-8')

        # Update the 'is_primary' field
        instance.is_primary = validated_data.get('is_primary', instance.is_primary)

        # Save the instance with updated values
        instance.save()
        return instance



# class UserCategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UsersCategory
#         fields = '__all__'             