# accounts/views.py
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from .serializers import UsersCategorySerializer
from .serializers import UpdateUsersCategorySerializer
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
import json
#from firebase_admin import initialize_app, _apps
import requests
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

from .models import UsersCategory
from .models import Chat
from users.models import Users
from django.db.models import Q
from wallet_resume.models import ResumeWallet
from connect.models import Connect
# from connect.models import Review
from connect.models import Notifications
from connect.models import Appointments

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import update_session_auth_hash
from django.db import IntegrityError
from fcm_django.models import FCMDevice

# import firebase_admin
# from firebase_admin import credentials, messaging

from datetime import time, datetime, timedelta
from django.http import JsonResponse
import subprocess


import math
import firebase_admin
from firebase_admin import credentials, messaging

# Path to your Firebase service account key
cred = credentials.Certificate("hustler_role_category/hustlersandseekers.json")

# Initialize the Firebase Admin app
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

# def haversine(lat1, lon1, lat2, lon2):
#     """
#     Calculate the great circle distance between two points
#     on the Earth's surface given their latitude and longitude
#     coordinates in decimal degrees.
#     """
#     # Convert latitude and longitude from degrees to radians
#     lat1_rad = math.radians(lat1)
#     lon1_rad = math.radians(lon1)
#     lat2_rad = math.radians(lat2)
#     lon2_rad = math.radians(lon2)

#     # Haversine formula
#     dlon = lon2_rad - lon1_rad
#     dlat = lat2_rad - lat1_rad
#     a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
#     c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
#     radius_of_earth_km = 6371  # Radius of the Earth in kilometers
#     radius_of_earth_miles = 3958.8  # Radius of the Earth in miles
#     distance_km = radius_of_earth_km * c
#     distance_miles = radius_of_earth_miles * c

#     return round(distance_miles, 2)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt

from .serializers import UsersCategorySerializer
from .models import UsersCategory

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def create_category(request):
    if request.method == 'POST':
        category_name = request.data.get('role_category_name')
        requested_user_id = request.data.get('user_id')  # Still read from body

        if not category_name:
            return Response(
                {"error": {"error_code": 400, "error": "role_category_name is required"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not requested_user_id:
            return Response(
                {"error": {"error_code": 400, "error": "user_id is required"}},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate: If requested user_id != logged-in user id -> Authentication error
        if str(request.user.id) != str(requested_user_id):
            return Response(
                {"error": {"error_code": 403, "error": "Permission denied: You cannot create a role for another user."}},
                status=status.HTTP_403_FORBIDDEN
            )


        user_id = request.user.id  # Safe

        # Check if the category already exists for this user
        if UsersCategory.objects.filter(user_id=user_id, role_category_name=category_name).exists():
            return Response(
                {"error": {"error_code": 409, "error": "Category already exists for this user"}},
                status=status.HTTP_409_CONFLICT
            )

        # Prepare the data to save
        data = {
            'user_id': requested_user_id,
            'role_category_name': category_name,
            'is_primary': request.data.get('is_primary', 0)  # default 0 if not given
        }

        serializer = UsersCategorySerializer(data=data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {"success": {"code": 200, "data": serializer.data}},
                status=status.HTTP_200_OK
            )

        return Response(
            {"error": {"error_code": 400, "error": serializer.errors}},
            status=status.HTTP_400_BAD_REQUEST
        )

import base64
import binascii
import re
import os
from django.conf import settings
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def update_category(request):
    base_url = 'http://82.25.86.49'
    user_id = request.data.get('user_id')
    category_id=request.data.get('id')
    category_name=request.data.get('role_category_name')
    if str(request.user.id) != str(user_id):
            return Response(
                {"error": {"error_code": 403, "error": "Permission denied: You cannot update another user category"}},
                status=status.HTTP_403_FORBIDDEN
            )


    category_instance = UsersCategory.objects.filter(user_id=user_id,id=category_id).first()
    if not category_instance:
        return Response({"error": {"error_code": 409, "error": "userid or catgeory id or catgeory name doesnt match with database"}},
                            status=status.HTTP_409_CONFLICT)
    print(category_instance)

    serializer = UpdateUsersCategorySerializer(instance=category_instance, data=request.data)

    if serializer.is_valid():
        serializer.save()

        def save_base64_image(base64_data, image_name):
            if not base64_data:
                return None

            try:
                if base64_data.startswith('data:image'):
                    base64_data = base64_data.split(';base64,')[-1]

                # Fix padding if needed
                padding_needed = (4 - len(base64_data) % 4) % 4
                base64_data += '=' * padding_needed

                image_data = base64.b64decode(base64_data)
                image_path = os.path.join(settings.MEDIA_ROOT, 'hustler_images', image_name)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)

                with open(image_path, 'wb') as f:
                    f.write(image_data)

                return f'hustler_images/{image_name}'

            except (binascii.Error, ValueError) as e:

                return None




        def save_base64_video(base64_data, video_name):
            if not base64_data:
                raise ValueError("No base64 video data provided.")

            try:
                if base64_data.startswith('data:video'):
                    base64_data = base64_data.split(';base64,')[-1]

                # Clean up unwanted characters and whitespace
                base64_data = base64_data.strip().replace('\n', '').replace('\r', '')
                base64_data = re.sub(r'[^A-Za-z0-9+/=]', '', base64_data)

                # Ensure proper base64 padding
                missing_padding = len(base64_data) % 4
                if missing_padding:
                    base64_data += '=' * (4 - missing_padding)

                video_data = base64.b64decode(base64_data)
            except Exception as e:
                return None

            # Save video
            video_path = os.path.join(settings.MEDIA_ROOT, 'hustler_videos', video_name)
            os.makedirs(os.path.dirname(video_path), exist_ok=True)

            with open(video_path, 'wb') as f:
                f.write(video_data)

            return f'hustler_videos/{video_name}'



        print(f"Image2 base64 length: {len(category_instance.image1)}")
        print(f"First 100 chars: {category_instance.image2[:100]}")
        print(f"Last 100 chars: {category_instance.image2[-100:]}")


        image1 = save_base64_image(category_instance.image1, f'{user_id}_{category_name}_image1.jpg') if category_instance.image1 else None
        image2 = save_base64_image(category_instance.image2, f'{user_id}_{category_name}_image2.jpg') if category_instance.image2 else None
        image3 = save_base64_image(category_instance.image3, f'{user_id}_{category_name}_image3.jpg') if category_instance.image3 else None
        video = save_base64_video(category_instance.video, f'{user_id}_{category_name}_video.mp4') if category_instance.video else None

        image1_url = f'{base_url}{settings.MEDIA_URL}{image1}' if image1 else None
        image2_url = f'{base_url}{settings.MEDIA_URL}{image2}' if image2 else None
        image3_url = f'{base_url}{settings.MEDIA_URL}{image3}' if image3 else None
        video_url = f'{base_url}{settings.MEDIA_URL}{video}' if video else None

        media_data = {
            "user_id": category_instance.user_id,
            "about_yourself": category_instance.about_yourself,
            "image1": image1_url,
            "image2": image2_url,
            "image3": image3_url,
            "video": video_url,
            "location": category_instance.location,
            "latitude": category_instance.latitude,
            "longitude": category_instance.longitude,
            "is_primary": category_instance.is_primary
        }

        return Response({
            "success": {
                "code": 200,
                "base_url": base_url,
                "data": media_data
            }
        }, status=status.HTTP_200_OK)


    return Response({
        "error": {
            "error_code": 400,
            "error": serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)



import os
import base64
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import UsersCategory  # Assuming UsersCategory is your model

# Base URL for your media files
base_url = 'http://82.25.86.49/'

# Function to save base64 image
import base64
import os
from django.conf import settings

def save_base64_image(base64_data, image_name):
    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(';base64,')[-1]

    # Fix padding
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)

    try:
        image_data = base64.b64decode(base64_data)
        image_path = os.path.join(settings.MEDIA_ROOT, 'hustler_images', image_name)
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        with open(image_path, 'wb') as f:
            f.write(image_data)

        return f'hustler_images/{image_name}'
    except:
        return None




# Function to save base64 video
import base64
import os
from django.conf import settings

import base64
import os
from django.conf import settings

def save_base64_video(base64_data, video_name):
    if base64_data.startswith('data:video'):
        base64_data = base64_data.split(';base64,')[-1]

    # Fix base64 padding if needed
    base64_data = base64_data.strip().replace('\n', '').replace('\r', '')
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)

    try:
        video_data = base64.b64decode(base64_data)
        video_path = os.path.join(settings.MEDIA_ROOT, 'hustler_videos', video_name)
        os.makedirs(os.path.dirname(video_path), exist_ok=True)

        with open(video_path, 'wb') as f:
            f.write(video_data)

        return f'hustler_videos/{video_name}'
    except:
       return None




from users.models import Users
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def role_category(request):
    data = request.data
    user_id = data.get('user_id')
    if str(request.user.id) != str(user_id):
            return Response(
                {"error": {"error_code": 403, "error": "Permission denied: You cannot fetch another user data"}},
                status=status.HTTP_403_FORBIDDEN
            )

    try:
        user = Users.objects.get(id=user_id)
    except Users.DoesNotExist:
        return Response({'status': 404, 'msg': 'User not found.'}, status=404)

    category_instances = UsersCategory.objects.filter(user_id=user_id)

    if not category_instances.exists():
        return Response({'status': 404, 'msg': 'User role category not found.'}, status=404)

    base_url = request.build_absolute_uri('/')  # Dynamic base URL from request
    profiles = []

    for instance in category_instances:
        category_name = instance.role_category_name.replace(" ", "_") if instance.role_category_name else "category"

        image1 = save_base64_image(instance.image1, f'{user_id}_{category_name}_image1.jpg') if instance.image1 else None
        image2 = save_base64_image(instance.image2, f'{user_id}_{category_name}_image2.jpg') if instance.image2 else None
        image3 = save_base64_image(instance.image3, f'{user_id}_{category_name}_image3.jpg') if instance.image3 else None
        video = save_base64_video(instance.video, f'{user_id}_{category_name}_video.mp4') if instance.video else None

        image1_url = f'{base_url}{settings.MEDIA_URL}{image1}' if image1 else None
        image2_url = f'{base_url}{settings.MEDIA_URL}{image2}' if image2 else None
        image3_url = f'{base_url}{settings.MEDIA_URL}{image3}' if image3 else None
        video_url = f'{base_url}{settings.MEDIA_URL}{video}' if video else None

        profiles.append({
            'id': instance.id,
            'name': user.name,
            'role_category_name': instance.role_category_name,
            'about_yourself': instance.about_yourself,
            'image1': image1_url,
            'image2': image2_url,
            'image3': image3_url,
            'video': video_url,
            'location': instance.location,
            'latitude': instance.latitude,
            'longitude': instance.longitude,
            'is_primary': instance.is_primary,
        })

    #return Response({'status': 200, 'data': profiles}, status=200)

    # Get all distinct categories
    allCategory = UsersCategory.objects.all().values('role_category_name').distinct()

    # Return the response with profile and categories
    return Response({
        'status': 200,
        'msg': 'User role category.',
        'base_url': base_url,
        'payload': profiles,
        'all_category':allCategory,

    })
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def Show_role_category(request):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'status': 400, 'msg': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    if str(request.user.id) != str(user_id):
            return Response(
                {"error": {"error_code": 403, "error": "Permission denied: You cannot fetch another user roles"}},
                status=status.HTTP_403_FORBIDDEN
            )

    # Get only distinct role_category_names for the specific user
    user_categories = UsersCategory.objects.filter(user_id=user_id).values_list('role_category_name', flat=True).distinct()

    return Response({
        'status': 200,
        'msg': 'Distinct role categories for the user.',
        'user_id': user_id,
        'role_categories': list(user_categories)
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def delete_category(request):
    user_id=request.user.id
    print(user_id)
    data = request.data
    profile = UsersCategory.objects.filter(id = data.get('category_id'),user_id=user_id).delete()
    return Response({'status':200,'msg':'Category deleted.'})


import math
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt

def haversine(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance using Haversine formula."""
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(6371 * c, 2)  # Distance in kilometers


import os
import base64
from django.conf import settings

def save_base64_image2(base64_data, image_name):

    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(';base64,')[-1]

    # Fix padding
    missing_padding = len(base64_data) % 4
    if missing_padding:
        base64_data += '=' * (4 - missing_padding)

    try:
        image_data = base64.b64decode(base64_data)
        image_path = os.path.join(settings.MEDIA_ROOT, 'user_images', image_name)

        # Ensure directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        with open(image_path, 'wb') as f:
            f.write(image_data)

        # Return relative path for MEDIA_URL use
        return f'user_images/{image_name}'
    except:
            return None





@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def top_profiles(request):
    data = request.data
    search_role=data['search_role']
    if str(request.user.id) != str(data['user_id']):
        return Response(
            {"error": {"error_code": 403, "error": "Permission denied: You cannot fetch another user roles"}},
            status=status.HTTP_403_FORBIDDEN
        )
    try:
        latitude1 = float(data['latitude'])
        longitude1 = float(data['longitude'])
    except (KeyError, ValueError):
        return Response({'status': 400, 'message': 'Invalid or missing latitude/longitude'})
    if search_role:
        profiles = UsersCategory.objects.filter(
            Q(role_category_name__icontains=search_role) & ~Q(user_id=data['user_id'])
        ).values(
            'id', 'user_id', 'role_category_name', 'summary', 'about_yourself',
            'price', 'latitude', 'longitude', 'image1', 'image2', 'image3', 'video',
            'twitter_link', 'isnta_link', 'fb_link', 'linkedin_link',
            'yt_link', 'other_link', 'is_primary'
        )
    else:
        profiles = UsersCategory.objects.filter(
            ~Q(user_id=data['user_id'])
        ).values(
            'id', 'user_id', 'role_category_name', 'summary', 'about_yourself',
            'price', 'latitude', 'longitude', 'image1', 'image2', 'image3', 'video',
            'twitter_link', 'isnta_link', 'fb_link', 'linkedin_link',
            'yt_link', 'other_link', 'is_primary'
        )
    temp_list = []

    for profile in profiles:
        userData = Users.objects.filter(id = profile['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'name' ,'location', 'banner_image', 'latitude', 'longitude')
        name=""

        if userData:
            userData = userData[0]

            image_path = save_base64_image2(userData['image'], f"{userData['id']}_profile_image.jpg") if userData.get('image') else None
            banner_path = save_base64_image2(userData['banner_image'], f"{userData['id']}_banner_image.jpg") if userData.get('banner_image') else None

            userData['image'] = f"{base_url}{settings.MEDIA_URL}{image_path}" if image_path else None
            userData['banner_image'] = f"{base_url}{settings.MEDIA_URL}{banner_path}" if banner_path else None
            name=userData['name']
        try:
            lat2 = float(profile['latitude'])
            lon2 = float(profile['longitude'])
            distance = haversine(latitude1, longitude1, lat2, lon2)
        except (TypeError, ValueError):
            distance = None
        if distance is not None and distance < 20:
            image1 = profile.get('image1')
            image2 = profile.get('image2')
            image3 = profile.get('image3')
            video = profile.get('video')

            image1_path = save_base64_image(image1, f"{profile['user_id']}_image1.jpg") if image1 else None
            image2_path = save_base64_image(image2, f"{profile['user_id']}_image2.jpg") if image2 else None
            image3_path = save_base64_image(image3, f"{profile['user_id']}_image3.jpg") if image3 else None
            video_path = save_base64_video(video, f"{profile['user_id']}_video.mp4") if video else None

            profile_data = {
                'id': profile['id'],
                'user_id': profile['user_id'],
                'name':name,
                'user_data': userData,
                'role_category_name': profile['role_category_name'],
                'about_yourself': profile['about_yourself'],
                'image1': f"{base_url}{settings.MEDIA_URL}{image1_path}" if image1_path else None,
                'image2': f"{base_url}{settings.MEDIA_URL}{image2_path}" if image2_path else None,
                'image3': f"{base_url}{settings.MEDIA_URL}{image3_path}" if image3_path else None,
                'video': f"{base_url}{settings.MEDIA_URL}{video_path}" if video_path else None,
                'twitter_link': profile['twitter_link'],
                'isnta_link': profile['isnta_link'],
                'fb_link': profile['fb_link'],
                'linkedin_link': profile['linkedin_link'],
                'yt_link': profile['yt_link'],
                'other_link': profile['other_link'],
                'is_primary': profile['is_primary'],
                'latitude': profile['latitude'],
                'longitude': profile['longitude'],
                'distance': distance,
                'is_bookmark': ResumeWallet.objects.filter(
                    user_id=data['user_id'],
                    role_category_id=profile['id']
                ).exists()
            }
            temp_list.append(profile_data)
    if temp_list:

        return Response({'status': 200, 'message': 'Top profiles found', 'data': temp_list})
    else:
        return Response({'status': 200, 'message': 'No profiles found', 'data': temp_list})



@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@csrf_exempt
def connect(request):
    data = request.data
    if Connect.objects.filter(user_id=data['user_id'], role_category_id=data['role_category_id'], hustler_id=data['hustler_id']).exists():
        return Response({'status': 400, 'msg': 'Already requested'}, status=400)

    else:
        userData = Users.objects.filter(id = data['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
        hustlerData = Users.objects.filter(id = data['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
        userDataa = userData[0]
        hustlerDataa = hustlerData[0]
        connect.user_id = data['user_id']
        connect.role_category_id = data['role_category_id']
        connect.hustler_id = data['hustler_id']
        connect.status = 'pending'
        connect.save()

        notification_message = userDataa['username'] + ' wants to connect with you, check the message sent you.'
        seeker_notification_message = 'You wants to connect with '+hustlerDataa['username']+', check the message you sent.'

        message = messaging.Message(
                    token=hustlerDataa['device_token'],
                    notification=messaging.Notification(
                        title=f"{userDataa['username']} sent a connection request",
                        body=notification_message
                    ),
                    data={
                        "priority": "high",
                        "title": f"{userDataa['username']} sent a connection request",
                        "body": notification_message,
                        "message_id": connect['id'],
                        "sound": "app_sound.wav",
                        "content_available": "true"  # Must be a string
                    }
                )

        # Send the message
        response = messaging.send(message)
        
        notifications = Notifications()
        notifications.user_id = data['user_id']
        notifications.connect_id = connect.id
        notifications.hustler_id = data['hustler_id']
        notifications.notification = notification_message
        notifications.role_category_id = data['role_category_id']
        notifications.seeker_notification = seeker_notification_message
        notifications.notifica_type = 'connect'
        notifications.status = 'Pending'
        notifications.save()
        return Response({'status': 200, 'msg': 'Connection request sent.'})
    




@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
@csrf_exempt
def send_message(request):
    data = request.data

    print(f"Request data: {data}")  # Debugging the incoming data

    if str(request.user.id) != str(data['sender_id']):
        return Response({"error": {"error_code": 403, "error": "Permission denied."}}, status=403)

    try:
        chat = Chat(
            category_id=data['category_id'],
            category_name=data['category_name'],
            sender_id=data['sender_id'],
            receiver_id=data['receiver_id'],
            message=data['message'],
            status='0'
        )

        attachment_b64 = data.get('attachment')
        if attachment_b64:
            try:
                base64.b64decode(attachment_b64)
                chat.attachment = attachment_b64
            except Exception as e:
                print(f"Error decoding attachment: {e}")
                return Response({"error": "Invalid attachment format"}, status=400)

        chat.save()  # This is where the data should be saved

        print(f"Message saved with ID: {chat.id}")  # Confirming the message has been saved

        return Response({
            "status": 201,
            "msg": "Message sent successfully",
            "chat_id": chat.id,
            "created_at": chat.created_at
        }, status=201)
    except Exception as e:
        print(f"Error saving message: {e}")  # If saving fails, log the error
        return Response({"error": {"error_code": 500, "error": "Internal server error"}}, status=500)






from collections import defaultdict
def fix_base64_padding(b64_string):
    return b64_string + '=' * (-len(b64_string) % 4)

import base64
from uuid import uuid4

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def messages(request):
    base_url = "http://82.25.86.49"  # Ideally from settings
    user_id = int(request.data.get('user_id'))
    if str(request.user.id) != str(request.data.get('user_id')):
        return Response(
            {"error": {"error_code": 403, "error": "Permission denied: You cannot fetch another user data"}},
            status=status.HTTP_403_FORBIDDEN
        )
    all_chats = Chat.objects.filter(
        Q(sender_id=user_id) | Q(receiver_id=user_id)
    ).order_by('-created_at')

    grouped = {}

    for chat in all_chats:
        cat_id = chat.category_id
        cat_name = chat.category_name

        if str(chat.sender_id) == str(user_id):
            other_user_id = chat.receiver_id
        else:
            other_user_id = chat.sender_id

        if cat_id not in grouped:
            grouped[cat_id] = {
                "id": chat.id,
                "user_id": user_id,
                "category_id": cat_id,
                "category_name": cat_name,
                "inbox": {}
            }

        if other_user_id not in grouped[cat_id]["inbox"]:
            userData = Users.objects.filter(id=other_user_id).values(
                'id', 'username', 'email', 'phone', 'image', 'gender', 'dob',
                'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude'
            ).first()

            if userData:
                if userData['dob']:
                    userData['dob'] = userData['dob'].strftime('%Y-%m-%d') if hasattr(userData['dob'], 'strftime') else userData['dob']

                # Attachment handling
                attachment_path = None
                if chat.attachment:
                    try:
                        fixed_base64 = fix_base64_padding(chat.attachment.strip())
                        file_data = base64.b64decode(fixed_base64)
                        file_ext = detect_file_type(file_data)
                        file_name = f"{uuid4()}.{file_ext}"
                        save_dir = os.path.join(settings.MEDIA_ROOT, 'chat_attachments')
                        os.makedirs(save_dir, exist_ok=True)
                        full_path = os.path.join(save_dir, file_name)

                        with open(full_path, 'wb') as f:
                            f.write(file_data)

                        attachment_path = f"{base_url}/media/chat_attachments/{file_name}"
                    except Exception as e:
                        print(f"Attachment error: {e}")
                        attachment_path = None

                grouped[cat_id]["inbox"][other_user_id] = {
                    "id": chat.id,
                    "userData": userData,
                    "message": chat.message,
                    "attachment": attachment_path,
                    "status": str(chat.status),
                    "created_at": chat.created_at.strftime('%Y-%m-%d %I:%M %p') if chat.created_at else None,
                }

    for cat in grouped.values():
        cat["inbox"] = list(cat["inbox"].values())

    return Response({
        "status": 200,
        "msg": "Messages",
        "data": list(grouped.values())
    })




def detect_file_type(file_bytes):
    FILE_SIGNATURES = {
        'jpg': b'\xFF\xD8\xFF',
        'png': b'\x89\x50\x4E\x47',
        'gif': b'\x47\x49\x46\x38',
        'mp4': b'\x00\x00\x00\x18\x66\x74\x79\x70\x33\x67\x70\x35',
        'avi': b'\x52\x49\x46\x46',
        'pdf': b'\x25\x50\x44\x46',
        'doc': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
        'docx': b'\x50\x4B\x03\x04',
        'ppt': b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1',
        'pptx': b'\x50\x4B\x03\x04',
    }
    for ext, signature in FILE_SIGNATURES.items():
        if file_bytes.startswith(signature):
            return ext
    return 'txt'






@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def messages_list(request):
    data = request.data
    messages_data = Chat.objects.filter(
        (Q(sender_id=data['other_user_id']) & Q(receiver_id=data['user_id'])) |
        (Q(sender_id=data['user_id']) & Q(receiver_id=data['other_user_id']))
    ).values('id', 'category_id', 'category_name', 'sender_id', 'receiver_id', 'message', 'status', 'created_at', 'attachment')

    temp_list = []

    for i in messages_data:
        temp_dict = {
            'id': i['id'],
            'category_id': i['category_id'],
            'category_name': i['category_name'],
            'sender_id': i['sender_id'],
            'receiver_id': i['receiver_id'],
            'message': i['message'],
            'status': i['status'],
            'created_at': i['created_at'].strftime('%Y-%m-%d %I:%M %p'),
            'attachment': None  # default
        }
        # If base64 attachment exists
        if i['attachment']:
            try:
                # Decode the base64 string into raw bytes
                decoded_file = base64.b64decode(i['attachment'])

                # Log the first few bytes of the decoded file
                print(f"Decoded file first few bytes: {binascii.hexlify(decoded_file[:20])}")

                # Detect the file type manually using magic bytes
                extension = detect_file_type(decoded_file)

                if not extension:
                    extension = 'bin'  # Default to binary if the file type is not supported

                # Save the file with a unique name
                file_name = f"{uuid4().hex}.{extension}"
                media_path = os.path.join(settings.MEDIA_ROOT, 'chat_attachments', file_name)
                os.makedirs(os.path.dirname(media_path), exist_ok=True)

                with open(media_path, 'wb') as f:
                    f.write(decoded_file)

                # Construct the URL to access the file
                media_url = os.path.join(settings.MEDIA_URL, 'chat_attachments', file_name)
                temp_dict['attachment'] = request.build_absolute_uri(media_url)

            except Exception as e:
                temp_dict['attachment'] = None  # Fail silently or log the error
                print(f"Error processing file: {e}")
        temp_list.append(temp_dict)

    return Response({'status': 200, 'msg': 'Messages.', 'data': temp_list})


#-------------------------------------------------------------------Notifications----------------------------------------------------------------------------#

@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def send_notification(request):
    url = "https://fcm.googleapis.com/fcm/send"

    # Define the data to be sent in the notification
    data = {
        "to": "fW-Ubcj2TbKmfMy-GFeqIE:APA91bHmzVqYLHelGQHtTC_4iHrRlUxkqOe3YYU0vp_Xlm4UQS5VO26Fi_lAWrFpgj7zVIfPvnxk7o4LnX7tkYeuBmt833UaEkPBpxXLBWWRPePWfP5FcFi3ExeSgNyZa-LjbbFGC-md",
        "notification": {
            "body": "New announcement assigned",
            "priority": "high",
            "message_id": '1',
            "title": "hello",
            "sound": "app_sound.wav",
        },
        "data": {
            "priority": "high",
            "message_id": '1',
            "title": "hello",
            "body": "New announcement assignedaaaa",
            "sound": "app_sound.wav",
            "content_available": True
        }
    }

    # Convert the data dictionary to a JSON string
    payload = json.dumps(data)

    # Define the headers
    headers = {
        'Authorization': 'key=AAAAMmfUttw:APA91bEicOCYgsYiYAyA3frA-h9piGaMho_2eiKfu8DAHaWRlqC-UaIDIhOD_C2ucQgFp-MDWLpIdBSAm01UgvE0YQpE_P6dKQSA-LKpIOAJPsSb5tcuccXokECi0afnuqnjICHI7Yn9',
        'Content-Type': 'application/json'
    }

    # Send the POST request with the payload and headers
    response = requests.post(url, headers=headers, data=payload)

    # Return the response
    return Response({'status':200,'msg':'sent'})



@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def notifications(request):
    data = request.data
    profile = Notifications.objects.filter(user_id = data['user_id']).values('id', 'user_id', 'hustler_id', 'notification', 'role_category_id', 'seeker_notification', 'notifica_type', 'status', 'created_at')
    profile2 = Notifications.objects.filter(hustler_id = data['user_id']).values('id', 'user_id', 'hustler_id', 'notification', 'role_category_id', 'seeker_notification', 'notifica_type', 'status', 'created_at')

    temp_list = []
    for i in profile:
        userData = Users.objects.filter(id = i['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
        hustlerData = Users.objects.filter(id = i['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
        temp_dict = {}
        temp_dict['id'] = i['id']
        temp_dict['user_id'] = i['user_id']
        temp_dict['hustler_id'] = i['hustler_id']
        temp_dict['user_data'] = userData[0]
        temp_dict['hustler_data'] = hustlerData[0]
        temp_dict['notification'] = i['notification']
        temp_dict['seeker_notification'] = i['seeker_notification']
        temp_dict['notifica_type'] = i['notifica_type']
        temp_dict['role_category_id'] = i['role_category_id']
        temp_dict['status'] = i['status']
        temp_dict['created_at'] = i['created_at'].strftime('%Y-%m-%d %I:%M %p')
        temp_list.append(temp_dict)

    temp_list2 = []
    for i2 in profile2:
        userData2 = Users.objects.filter(id = i2['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
        hustlerData2 = Users.objects.filter(id = i2['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
        temp_dict2 = {}
        temp_dict2['id'] = i2['id']
        temp_dict2['user_id'] = i2['user_id']
        temp_dict2['hustler_id'] = i2['hustler_id']
        temp_dict2['user_data'] = userData2[0]
        temp_dict2['notification'] = i2['notification']
        temp_dict2['seeker_notification'] = i2['seeker_notification']
        temp_dict2['notifica_type'] = i2['notifica_type']
        temp_dict2['status'] = i2['status']
        temp_dict2['created_at'] = i2['created_at'].strftime('%Y-%m-%d %I:%M %p')
        temp_list2.append(temp_dict2)

    return Response({'status': 200, 'message': 'Notifications', 'hustlers': temp_list2, 'seekers': temp_list})


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def update_connect_status(request):
    data = request.data


    if Notifications.objects.filter(id=data['notification_id']).exists():
        noti_obj = Notifications.objects.filter(id = data['notification_id'])[0]
        noti_obj.status = data['status']
        noti_obj.save()

        userData = Users.objects.filter(id=noti_obj.user_id).values('device_token').first()
        hustlerData = Users.objects.filter(id=noti_obj.hustler_id).values('device_token').first()
        url = "https://fcm.googleapis.com/fcm/send"
        if userData and hustlerData:
           # Create the message
            message = messaging.Message(
                token=userData['device_token'],
                notification=messaging.Notification(
                    title='Your request is ' + data['status'],
                    body='Your request is ' + data['status'],
                ),
                data={
                    'priority': 'high',
                    'title': 'Your request is ' + data['status'],
                    'body': 'Your request is ' + data['status'],
                    'message_id': data['notification_id'],
                    'sound': 'app_sound.wav',
                    'content_available': 'true',
                },
            )

            # Send the message
            response = messaging.send(message)
            print("✅ Successfully sent message:", response)
        else:

            return Response({'status': 200, 'msg': 'Notification id not correct'})



        if data['type'] == "connect":

            if data['status'] == 'Accepted':
                conn_obj = Connect.objects.filter(id = noti_obj.connect_id)[0]
                conn_obj.status = 'Accepted'
                conn_obj.save()
                return Response({'status': 200, 'msg': 'Request Accepted'})
            else:
                Notifications.objects.filter(id = data['notification_id']).delete()
                Connect.objects.filter(id = noti_obj.connect_id).delete()
                return Response({'status': 200, 'msg': 'Request Rejected'})
        else:

            if data['status'] == 'Accepted':
                # conn_obj1 = Appointments.objects.filter(id = noti_obj.connect_id)[0]
                # conn_obj1.status = 'Accepted'
                # conn_obj1.save()
                return Response({'status': 200, 'msg': 'Request Accepted'})
            else:
                # Notifications.objects.filter(id = data['notification_id']).delete()
                # Appointments.objects.filter(id = data['notification_id']).delete()
                # Connect.objects.filter(id = noti_obj.connect_id).delete()
                return Response({'status': 200, 'msg': 'Request Rejected'})


    else:

        return  Response({'status': 400, 'msg': 'Notification id not correct.'})

from serpapi import GoogleSearch


from serpapi import GoogleSearch

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def youtube_shorts_search(request):
    data = request.data
    query = data.get('query')

    if not query:
        return JsonResponse({"error": "Missing search query parameter."}, status=400)

    params = {
        "engine": "youtube",
        "search_query": query,
        "api_key": "0958fdb5c7fdb651a8c42f32aa3530a07ff7c566a991f9b164368e3a0f061434"
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()

        video_results = results.get("video_results", [])

        shorts_results = results.get("shorts_results", [])
        all_shorts = []
        for section in shorts_results:
            all_shorts.extend(section.get("shorts", []))

        channels_new_to_you = results.get("channels_new_to_you", [])
        people_also_search_for = results.get("people_also_search_for", {}).get("searches", [])
        from_related_searches = results.get("from_related_searches", [])

        return JsonResponse({
            "video_results": video_results,
            "shorts_results": all_shorts,
            "channels_new_to_you": channels_new_to_you,
            "people_also_search_for": people_also_search_for,
            "from_related_searches": from_related_searches
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": f"Internal Server Error: {str(e)}"}, status=500)
# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def mini_resume(request):
#     data = request.data
#     latitude1 = int(float(data['latitude']))
#     longitude1 = int(float(data['longitude']))

#     profile = ResumeWallet.objects.filter(user_id=data['user_id']).values('id', 'user_id', 'role_category_name').distinct('role_category_name')
#     temp_list = []

#     for i in profile:
#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['user_id'] = i['user_id']
#         temp_dict['role_category_name'] = i['role_category_name']
#         temp_dict['bookmarks'] = []

#         if ResumeWallet.objects.filter(role_category_name=i['role_category_name'], user_id=data['user_id']).exists():
#             bookmarks = ResumeWallet.objects.filter(user_id=data['user_id'], role_category_name=i['role_category_name']).values('id', 'user_id', 'role_category_id', 'role_category_name')

#             for bookmark in bookmarks:
#                 userData = Users.objects.filter(id=bookmark['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#                 category = UsersCategory.objects.filter(id=bookmark['role_category_id']).values('id', 'user_id', 'role_category_name', 'summary', 'about_yourself', 'price', 'image1', 'image2', 'image3', 'video', 'twitter_link', 'isnta_link', 'fb_link', 'linkedin_link', 'yt_link', 'other_link', 'is_primary')
#                 category = category[0]
#                 userData = userData[0]
#                 temp_dict2 = {}
#                 temp_dict2['id'] = category['id']
#                 temp_dict2['user_id'] = category['user_id']
#                 temp_dict2['user_data'] = userData
#                 temp_dict2['role_category_name'] = category['role_category_name']
#                 temp_dict2['summary'] = category['summary']
#                 temp_dict2['about_yourself'] = category['about_yourself']
#                 temp_dict2['price'] = category['price']
#                 temp_dict2['image1'] = category['image1']
#                 temp_dict2['image2'] = category['image2']
#                 temp_dict2['image3'] = category['image3']
#                 temp_dict2['video'] = category['video']
#                 temp_dict2['twitter_link'] = category['twitter_link']
#                 temp_dict2['isnta_link'] = category['isnta_link']
#                 temp_dict2['fb_link'] = category['fb_link']
#                 temp_dict2['linkedin_link'] = category['linkedin_link']
#                 temp_dict2['yt_link'] = category['yt_link']
#                 temp_dict2['other_link'] = category['other_link']
#                 temp_dict2['is_primary'] = category['is_primary']

#                 temp_dict['bookmarks'].append(temp_dict2)

#         temp_list.append(temp_dict)

#     return Response({'status': 200, 'msg': 'User category.', 'base_url': 'https://hustlersandseekers.co/hustler/media/', 'data': temp_list})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def add_to_wallet(request):
#     data = request.data
#     resumeWallet = ResumeWallet();
#     if ResumeWallet.objects.filter(user_id = data['user_id'], role_category_id = data['role_category_id']).exists():
#         ResumeWallet.objects.filter(user_id = data['user_id'], role_category_id = data['role_category_id']).delete()
#         return Response({'status':200,'msg':'Removed from wallet.'})
#     else:
#         category = UsersCategory.objects.filter(id = data['role_category_id']).values('id', 'role_category_name')
#         resumeWallet.user_id = data['user_id']
#         resumeWallet.role_category_id = data['role_category_id']
#         resumeWallet.role_category_name = category[0]['role_category_name']
#         resumeWallet.save()
#         return Response({'status':200, 'msg':'Added to your wallet.'})




# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def top_videos(request):
#     data = request.data

#     latitude1 = int(float(data['latitude']))
#     longitude1 = int(float(data['longitude']))

#     # Fetch profile data with non-empty videos
#     profile = UsersCategory.objects.filter(~Q(video__exact='')).values('id', 'user_id', 'video', 'created_at').order_by('-created_at')

#     # Fetch posts data with non-empty videos
#     posts = UsersPosts.objects.filter(~Q(video__exact='')).values('id', 'user_id', 'summary', 'video', 'created_at').order_by('-created_at')

#     # Combine profile and posts data
#     combined_data = list(profile) + list(posts)

#     # Sort combined data based on created_at field in descending order
#     combined_data.sort(key=lambda x: x['created_at'], reverse=True)

#     temp_list = []

#     for entry in combined_data:
#         # Fetch user data for the entry
#         user_data = Users.objects.filter(id=entry['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')

#         if user_data:
#             userData = user_data[0]
#             if userData['latitude']:
#                 latitude2 = int(float(userData['latitude']))
#                 longitude2 = int(float(userData['longitude']))
#                 distance = haversine(latitude1, longitude1, latitude2, longitude2)
#             else:
#                distance = 0
#         else:
#             distance = 0
#         if distance < 20:
#             temp_dict = {}
#             temp_dict['id'] = entry['id']
#             temp_dict['user_id'] = entry['user_id']
#             temp_dict['user_data'] = userData if userData else {}  # Ensure user_data exists before accessing index 0
#             temp_dict['summary'] = entry.get('summary', '')
#             temp_dict['video'] = entry['video']
#             temp_dict['created_at'] = entry['created_at'].strftime('%Y-%m-%d %I:%M %p')

#             temp_list.append(temp_dict)

#     return Response({'status': 200, 'message': 'Top videos', 'data': temp_list})


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def add_review(request):
#     data = request.data
#     review = Review();
#     if Review.objects.filter(user_id = data['user_id'], hustler_id = data['hustler_id'], role_id = data['role_id']).exists():
#         return Response({'status':400,'msg':'Already Reviewed.'})
#     else:
#         review.user_id = data['user_id']
#         review.hustler_id = data['hustler_id']
#         review.role_id = data['role_id']
#         review.review = data['review']
#         review.rating = data['rating']
#         review.save()
#         return Response({'status':200, 'msg':'success.'})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def top_reviews(request):
#     data = request.data
#     profile = Review.objects.filter(hustler_id=data['user_id']).values('id', 'user_id', 'hustler_id', 'role_id', 'review', 'rating').order_by('-created_at')
#     # profile = Review.objects.all().values('id', 'user_id', 'hustler_id', 'role_id', 'review', 'rating').order_by('-created_at')[:5]
#     temp_list = []
#     for i in profile:
#         userData = Users.objects.filter(id = i['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         hustlerData = Users.objects.filter(id = i['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['user_id'] = i['user_id']
#         temp_dict['hustler_id'] = i['hustler_id']
#         temp_dict['user_data'] = userData[0]
#         temp_dict['hustler_Data'] = hustlerData[0]
#         temp_dict['role_id'] = i['role_id']
#         temp_dict['review'] = i['review']
#         temp_dict['rating'] = i['rating']
#         temp_list.append(temp_dict)
#     return Response({'status': 200, 'message': 'Top Reviews', 'data': temp_list})



# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def hustler_links(request):
#     data = request.data
#     if UsersCategory.objects.filter(user_id = data['hustler_id'], id = data['role_category_id']).exists():
#         noti_obj = UsersCategory.objects.filter(user_id = data['hustler_id'], id = data['role_category_id']).values('id', 'user_id', 'role_category_name', 'price', 'twitter_link', 'isnta_link', 'fb_link', 'linkedin_link', 'other_link', 'yt_link')
#         noti_objs = noti_obj[0]
#         hustlerData = Users.objects.filter(id = data['hustler_id']).values('id', 'username', 'image', 'location', 'latitude', 'longitude')
#         hustlerDataa = hustlerData[0]
#         noti_objs['username'] = hustlerDataa['username']
#         noti_objs['image'] = hustlerDataa['image']
#         noti_objs['location'] = hustlerDataa['location']
#         return Response({'status': 200, 'msg': 'hustler links', 'data':noti_objs})
#     else:

#         return Response({'status': 400, 'msg': 'Something went wrong.'})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def booking_appointment(request):
#     data = request.data
#     Appointment = Appointments();
#     if Appointments.objects.filter(user_id = data['user_id'], hustler_id = data['hustler_id'], role_id = data['role_id'], date = data['date'], start_time = data['start_time'], end_time = data['end_time']).exists():
#         return Response({'status':400,'msg':'Already have booking on this slot Please choose other slot.'})
#     else:
#         userData = Users.objects.filter(id = data['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
#         hustlerData = Users.objects.filter(id = data['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
#         if userData:
#             userDataa = userData[0]
#         else:
#             userDataa = userData
#         if hustlerData:
#             hustlerDataa = hustlerData[0]
#         else:
#             hustlerDataa = hustlerData

#         Appointment.user_id = data['user_id']
#         Appointment.hustler_id = data['hustler_id']
#         Appointment.role_id = data['role_id']
#         Appointment.date = data['date']
#         Appointment.start_time = data['start_time']
#         Appointment.end_time = data['end_time']
#         Appointment.where = data['where']
#         Appointment.hustle = data['hustle']
#         Appointment.price = data['price']
#         Appointment.modified_by = ''
#         Appointment.status = 'pending'
#         Appointment.save()

#         notification_message = userDataa['username'] + ' has requested to you for appointment.'
#         seeker_notification_message = 'You have successfully requested an appointment with '+hustlerDataa['username']

#         url = "https://fcm.googleapis.com/fcm/send"

#         # Define the data to be sent in the notification
#         dataa = {
#             "to": hustlerDataa['device_token'],
#             "notification": {
#                 "body": notification_message,
#                 "priority": "high",
#                 "message_id": Appointment.id,
#                 "title": userDataa['username']+' sent a appointment request',
#                 "sound": "app_sound.wav",
#             },
#             "data": {
#                 "priority": "high",
#                 "title": userDataa['username']+' sent a appointment request',
#                 "body": notification_message,
#                 "message_id": Appointment.id,
#                 "sound": "app_sound.wav",
#                 "content_available": True
#             }
#         }

#         # Convert the data dictionary to a JSON string
#         payload = json.dumps(dataa)

#         # Define the headers
#         headers = {
#             'Authorization': 'key=AAAAMmfUttw:APA91bFl7CTYHRar2M4KAY_GskDEfApLqawNehtyL7_vjNWsF476TAwT1a3Rf5PNkS2F9D6tTUzC8cShbvRYukWU5STpEkeiiIld0Yd8OnBQLL8heqfYfOeNqjCYJxnh_LNhCwmlx-4P',
#             'Content-Type': 'application/json'
#         }

#         # Send the POST request with the payload and headers
#         response = requests.post(url, headers=headers, data=payload)

#         notifications = Notifications();
#         notifications.user_id = data['user_id']
#         notifications.connect_id = Appointment.id
#         notifications.hustler_id = data['hustler_id']
#         notifications.notification = notification_message
#         notifications.role_category_id = data['role_id']
#         notifications.seeker_notification = seeker_notification_message
#         notifications.notifica_type = 'appointment'
#         notifications.status = 'Pending'
#         notifications.save()

#         if Notifications.objects.filter(id=data['notification_id']).exists():
#             noti_obj = Notifications.objects.filter(id = data['notification_id'])[0]
#             noti_obj.status = 'Booked'
#             noti_obj.save()
#         else:
#             return Response({'status': 400, 'msg': 'Something went wrong.'})
#         return Response({'status':200, 'msg':'Appointment booked successfully.'})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def all_appointments(request):
#     data = request.data
#     profile = Appointments.objects.filter(Q(user_id=data['user_id']) | Q(hustler_id=data['user_id']), date=data['date']).values('id', 'user_id', 'hustler_id', 'role_id', 'date', 'start_time', 'end_time', 'where', 'hustle', 'price', 'modified_by', 'status', 'created_at', 'updated_at').order_by('-created_at')
#     temp_list = []
#     for i in profile:
#         userData = Users.objects.filter(id = i['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         hustlerData = Users.objects.filter(id = i['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['user_id'] = i['user_id']
#         temp_dict['hustler_id'] = i['hustler_id']
#         temp_dict['user_data'] = userData[0]
#         temp_dict['hustler_Data'] = hustlerData[0]
#         temp_dict['role_id'] = i['role_id']
#         temp_dict['date'] = i['date']
#         temp_dict['start_time'] = i['start_time']
#         temp_dict['end_time'] = i['end_time']
#         temp_dict['where'] = i['where']
#         temp_dict['hustle'] = i['hustle']
#         temp_dict['price'] = i['price']
#         temp_dict['modified_by'] = i['modified_by']
#         temp_dict['created_at'] = i['created_at'].strftime('%Y-%m-%d %I:%M %p')
#         temp_dict['updated_at'] = i['updated_at'].strftime('%Y-%m-%d %I:%M %p')
#         temp_list.append(temp_dict)
#     return Response({'status': 200, 'message': 'All Appointments', 'data': temp_list})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def get_hustler_slots(request):

#     data = request.data
#     temp_list = []
#     current_time = datetime.now().time()
#     for hour in range(1, 24):
#         time_slot = time(hour, 0, 0)
#         datetime_slot = datetime.combine(datetime.today(), time_slot)
#         next_hour_datetime = datetime_slot + timedelta(hours=1)
#         next_hour_time = next_hour_datetime.time()
#         formatted_time = datetime_slot.time().strftime('%H:%M:%S')
#         next_hour_formatted_time = next_hour_time.strftime('%H:%M:%S')
#         if datetime.strptime(formatted_time, '%H:%M:%S').time() > current_time:

#             if Appointments.objects.filter(hustler_id=data['hustler_id'], date=data['date'], start_time=formatted_time).exists():

#                 temp_dict = {
#                     'start_times': formatted_time,
#                     'end_time': next_hour_formatted_time,
#                     'is_available': 0
#                 }
#             else:
#                 temp_dict = {
#                     'start_times': formatted_time,
#                     'end_time': next_hour_formatted_time,
#                     'is_available': 1
#                 }
#             temp_list.append(temp_dict)

#     return JsonResponse({'status': 200, 'message': 'All slots', 'data': temp_list})

# @api_view(['POST'])


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def delete_category(request):
#     data = request.data
#     profile = UsersCategory.objects.filter(id = data.get('category_id')).delete()
#     return Response({'status':200,'msg':'Category deleted.'})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def add_post(request):
#     data = request.data
#     UsersPost = UsersPosts();

#     UsersPost.user_id = data['user_id']
#     UsersPost.summary = data['text']
#     UsersPost.video = data['file']
#     UsersPost.save()
#     return Response({'status':200, 'msg':'Posted successfully.'})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def get_distance(request):
#     latitude1 = 52.5200  # Latitude of Point 1 (Berlin, Germany)
#     longitude1 = 13.4050  # Longitude of Point 1 (Berlin, Germany)
#     latitude2 = 48.8566  # Latitude of Point 2 (Paris, France)
#     longitude2 = 2.3522  # Longitude of Point 2 (Paris, France)

#     distance = haversine(latitude1, longitude1, latitude2, longitude2)
#     mess = "Distance between Berlin and Paris:", distance, "miles"
#     return Response({'status':200, 'msg':mess})

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def send_message(request):
#     data = request.data
#     chats = Chat()
#     chats.category_id = data['category_id']
#     chats.category_name = data['category_name']
#     chats.sender_id = data['sender_id']
#     chats.receiver_id = data['receiver_id']
#     chats.message = data['message']
#     chats.status = '0'
#     chats.save()

#     url = "https://fcm.googleapis.com/fcm/send"
#     userData = Users.objects.filter(id=data['receiver_id']).values('id', 'device_token')[0]
#     senderData = Users.objects.filter(id=data['sender_id']).values('id', 'username', 'device_token')[0]

#     # Define the data to be sent in the notification
#     data = {
#         "to": userData['device_token'],
#         "notification": {
#             "body": data['message'],
#             "priority": "high",
#             "message_id": chats.id,
#             "title": senderData['username']+' sent a message',
#             "sound": "app_sound.wav",
#         },
#         "data": {
#             "priority": "high",
#             "title": senderData['username']+' sent a message',
#             "body": data['message'],
#             "message_id": chats.id,
#             "sound": "app_sound.wav",
#             "content_available": True
#         }
#     }

#     # Convert the data dictionary to a JSON string
#     payload = json.dumps(data)

#     # Define the headers
#     headers = {
#         'Authorization': 'key=AAAAMmfUttw:APA91bFl7CTYHRar2M4KAY_GskDEfApLqawNehtyL7_vjNWsF476TAwT1a3Rf5PNkS2F9D6tTUzC8cShbvRYukWU5STpEkeiiIld0Yd8OnBQLL8heqfYfOeNqjCYJxnh_LNhCwmlx-4P',
#         'Content-Type': 'application/json'
#     }

#     # Send the POST request with the payload and headers
#     response = requests.post(url, headers=headers, data=payload)
#     return Response({'status': 200, 'msg': 'message sent.'})

