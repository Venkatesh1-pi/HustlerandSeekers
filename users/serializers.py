from rest_framework import serializers
from .models import Users
from django.db import IntegrityError

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'password', 'phone', 'location', 'latitude', 'longitude']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        user = Users(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            location=validated_data['location'],
            latitude=validated_data['latitude'],
            longitude=validated_data['longitude'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

from rest_framework import serializers
from django.db import IntegrityError
from .models import Users
import base64

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = [
            'id', 'username', 'name', 'email', 'phone',
            'image', 'gender', 'dob', 'location',
            'banner_image', 'latitude', 'longitude', 'radius_km'
        ]

    def update(self, instance, validated_data):
        try:
            instance.username = validated_data.get('username', instance.username)
            instance.name = validated_data.get('name', instance.name)
            instance.email = validated_data.get('email', instance.email)
            instance.phone = validated_data.get('phone', instance.phone)
            instance.gender = validated_data.get('gender', instance.gender)
            instance.dob = validated_data.get('dob', instance.dob)
            instance.location = validated_data.get('location', instance.location)
            instance.latitude = validated_data.get('latitude', instance.latitude)
            instance.longitude = validated_data.get('longitude', instance.longitude)
            instance.radius_km = validated_data.get('radius_km', instance.radius_km)

            if 'image' in validated_data:
                instance.image = validated_data['image']
            if 'banner_image' in validated_data:
                instance.banner_image = validated_data['banner_image']

                instance.save()

        except IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                self.fail('username_exists')
            else:
                raise e

        return instance



class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ResetPasswordEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True) 
