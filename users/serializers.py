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

class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude', 'radius_km']

    def update(self, instance, validated_data):
        try:
            # Update the fields of the instance with the validated data
            instance.username = validated_data.get('username', instance.username)
            instance.email = validated_data.get('email', instance.email)
            instance.phone = validated_data.get('phone', instance.phone)
            instance.image = validated_data.get('image', instance.image)
            instance.banner_image = validated_data.get('banner_image', instance.banner_image)
            instance.gender = validated_data.get('gender', instance.gender)
            instance.dob = validated_data.get('dob', instance.dob)
            instance.first_name = validated_data.get('first_name', instance.first_name)  # Corrected line
            instance.last_name = validated_data.get('last_name', instance.last_name)  # Corrected line
            instance.location = validated_data.get('location', instance.location)
            instance.latitude = validated_data.get('latitude', instance.latitude)
            instance.longitude = validated_data.get('longitude', instance.longitude)
            instance.radius_km = validated_data.get('radius_km', instance.radius_km)  # Update the radius_km field

            # Save the instance to persist the changes
            instance.save()

        except IntegrityError as e:
            # Handle unique constraint violation
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
