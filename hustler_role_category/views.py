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
from .models import UsersPosts
from .models import Chat
from users.models import Users
from django.db.models import Q
#from wallet_resume.models import ResumeWallet
# from connect.models import Connect
# from connect.models import Review
# from connect.models import Notifications
# from connect.models import Appointments

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

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the Earth's surface given their latitude and longitude
    coordinates in decimal degrees.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Haversine formula
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    radius_of_earth_km = 6371  # Radius of the Earth in kilometers
    radius_of_earth_miles = 3958.8  # Radius of the Earth in miles
    distance_km = radius_of_earth_km * c
    distance_miles = radius_of_earth_miles * c

    return round(distance_miles, 2)
from rest_framework import status
from rest_framework.response import Response
from .serializers import UsersCategorySerializer
from .models import UsersCategory  # Assuming the model is named Category
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt


def create_category(request):
    if request.method == 'POST':
        # Assuming 'category_name' is a unique field in the Category model
        category_name = request.data.get('role_category_name')  # Change to the correct field name
        
        # Check if the category already exists
        # if UsersCategory.objects.filter(role_category_name=category_name).exists():
        #     return Response({"error": {"error_code": 409, "error": "Category already exists"}}, 
        #                     status=status.HTTP_409_CONFLICT)
        
        # If the category does not exist, create a new one
        serializer = UsersCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": {"code": 200, "data": serializer.data}}, 
                            status=status.HTTP_200_OK)
        
        return Response({"error": {"error_code": 400, "error": serializer.errors}}, 
                        status=status.HTTP_400_BAD_REQUEST)

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
    base_url = 'http://127.0.0.1:8000'
    user_id = request.data.get('user_id')  # Use 'user_id' for consistency
    category_id=request.data.get('id')
    category_name=request.data.get('role_category_name')
    print(f"User ID: {user_id}")  # Debugging

    try:
        category_instance = UsersCategory.objects.filter(user_id=user_id, role_category_name=category_name,id=int(category_id)).first()
    except UsersCategory.DoesNotExist:
        return Response({
            "error": {
                "error_code": 404,
                "error": "User category not found"
            }
        }, status=status.HTTP_404_NOT_FOUND)
    
    print(category_instance)
    if category_instance:
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

            except (binascii.Error, ValueError) as e:
                # Log the error and return None or handle as per your need
                print(f"[Warning] Skipping invalid image {image_name}: {e}")
                return None

            image_path = os.path.join(settings.MEDIA_ROOT, 'hustler_images', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)

            with open(image_path, 'wb') as f:
                f.write(image_data)

            return f'hustler_images/{image_name}'



        
        def save_base64_video(base64_data, video_name):
            if base64_data.startswith('data:video'):
                base64_data = base64_data.split(';base64,')[-1]

            # Decode the base64 video data
            video_data = base64.b64decode(base64_data)

            # Set the video save path
            video_path = os.path.join(settings.MEDIA_ROOT, 'hustler_videos', video_name)

            # Ensure the directory exists
            os.makedirs(os.path.dirname(video_path), exist_ok=True)

            # Write the video data to the file
            with open(video_path, 'wb') as f:
                f.write(video_data)

            # Return the relative path for MEDIA_URL use
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
base_url = 'http://127.0.0.1:8000/'

# Function to save base64 image
def save_base64_image(base64_data, image_name):
    if base64_data.startswith('data:image'):
        base64_data = base64_data.split(';base64,')[-1]

    image_data = base64.b64decode(base64_data)
    image_path = os.path.join(settings.MEDIA_ROOT, 'hustler_images', image_name)

    # Ensure directory exists
    os.makedirs(os.path.dirname(image_path), exist_ok=True)

    # Save the image data to the file
    with open(image_path, 'wb') as f:
        f.write(image_data)

    # Return the relative path for MEDIA_URL use
    return f'hustler_images/{image_name}'

# Function to save base64 video
def save_base64_video(base64_data, video_name):
    if base64_data.startswith('data:video'):
        base64_data = base64_data.split(';base64,')[-1]

    # Decode the base64 video data
    video_data = base64.b64decode(base64_data)

    # Set the video save path
    video_path = os.path.join(settings.MEDIA_ROOT, 'hustler_videos', video_name)

    # Ensure the directory exists
    os.makedirs(os.path.dirname(video_path), exist_ok=True)

    # Save the video data to the file
    with open(video_path, 'wb') as f:
        f.write(video_data)

    # Return the relative path for MEDIA_URL use
    return f'hustler_videos/{video_name}'
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

    # Get only distinct role_category_names for the specific user
    user_categories = UsersCategory.objects.filter(user_id=user_id).values_list('role_category_name', flat=True).distinct()

    return Response({
        'status': 200,
        'msg': 'Distinct role categories for the user.',
        'user_id': user_id,
        'role_categories': list(user_categories)
    }, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def top_profiles(request):
#     data = request.data
#     latitude1 = int(float(data['latitude']))
#     longitude1 = int(float(data['longitude']))
#     profile = UsersCategory.objects.all().values('id', 'user_id', 'role_category_name', 'summary', 'about_yourself', 'price', 'image1', 'image2', 'image3', 'video', 'twitter_link', 'isnta_link', 'fb_link', 'linkedin_link', 'yt_link', 'other_link', 'is_primary')
#     temp_list = []
#     for i in profile:
#         userData = Users.objects.filter(id = i['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         if userData:
#             userData = userData[0]
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
#             temp_dict['id'] = i['id']
#             temp_dict['user_id'] = i['user_id']
#             temp_dict['user_data'] = userData
#             temp_dict['role_category_name'] = i['role_category_name']
#             temp_dict['summary'] = i['summary']
#             temp_dict['about_yourself'] = i['about_yourself']
#             temp_dict['price'] = i['price']
#             temp_dict['image1'] = i['image1']
#             temp_dict['image2'] = i['image2']
#             temp_dict['image3'] = i['image3']
#             temp_dict['video'] = i['video']
#             temp_dict['twitter_link'] = i['twitter_link']
#             temp_dict['isnta_link'] = i['isnta_link']
#             temp_dict['fb_link'] = i['fb_link']
#             temp_dict['linkedin_link'] = i['linkedin_link']
#             temp_dict['yt_link'] = i['yt_link']
#             temp_dict['other_link'] = i['other_link']
#             temp_dict['is_primary'] = i['is_primary']
#             temp_dict['distance'] = distance
#             if ResumeWallet.objects.filter(user_id = data['user_id'] , role_category_id = i['id']).exists():
#                 temp_dict['is_bookmark'] = "True"
#             else:
#                 temp_dict['is_bookmark'] = "False"
#             temp_list.append(temp_dict)
#     return Response({'status': 200, 'message': 'Top profile', 'data': temp_list}) 

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
# def connect(request):
#     data = request.data
#     connect = Connect()

#     if Connect.objects.filter(user_id=data['user_id'], role_category_id=data['role_category_id'], hustler_id=data['hustler_id']).exists():

#         return Response({'status': 400, 'msg': 'Already requested'})
#     else:
#         userData = Users.objects.filter(id = data['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
#         hustlerData = Users.objects.filter(id = data['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'device_token', 'latitude', 'longitude')
#         userDataa = userData[0]
#         hustlerDataa = hustlerData[0]
#         connect.user_id = data['user_id']
#         connect.role_category_id = data['role_category_id']
#         connect.hustler_id = data['hustler_id']
#         connect.status = 'pending'
#         connect.save()

#         notification_message = userDataa['username'] + ' wants to connect with you, check the message sent you.'
#         seeker_notification_message = 'You wants to connect with '+hustlerDataa['username']+', check the message you sent.'
        
#         url = "https://fcm.googleapis.com/fcm/send"

#         # Define the data to be sent in the notification
#         dataa = {
#             "to": hustlerDataa['device_token'],
#             "notification": {
#                 "body": notification_message,
#                 "priority": "high",
#                 "message_id": connect.id,
#                 "title": userDataa['username']+' sent a connection request',
#                 "sound": "app_sound.wav",
#             },
#             "data": {
#                 "priority": "high",
#                 "title": userDataa['username']+' sent a connection request',
#                 "body": notification_message,
#                 "message_id": connect.id,
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
#         notifications.connect_id = connect.id
#         notifications.hustler_id = data['hustler_id']
#         notifications.notification = notification_message
#         notifications.role_category_id = data['role_category_id']
#         notifications.seeker_notification = seeker_notification_message
#         notifications.notifica_type = 'connect'
#         notifications.status = 'Pending'
#         notifications.save()
#         return Response({'status': 200, 'msg': 'Connection request sent.'})
    

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
# def notifications(request):
#     data = request.data
#     profile = Notifications.objects.filter(user_id = data['user_id']).values('id', 'user_id', 'hustler_id', 'notification', 'role_category_id', 'seeker_notification', 'notifica_type', 'status', 'created_at')
#     profile2 = Notifications.objects.filter(hustler_id = data['user_id']).values('id', 'user_id', 'hustler_id', 'notification', 'role_category_id', 'seeker_notification', 'notifica_type', 'status', 'created_at')
    
#     temp_list = []
#     for i in profile:
#         userData = Users.objects.filter(id = i['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         hustlerData = Users.objects.filter(id = i['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['user_id'] = i['user_id']
#         temp_dict['hustler_id'] = i['hustler_id']
#         temp_dict['user_data'] = userData[0]
#         temp_dict['hustler_data'] = hustlerData[0]
#         temp_dict['notification'] = i['notification']
#         temp_dict['seeker_notification'] = i['seeker_notification']
#         temp_dict['notifica_type'] = i['notifica_type']
#         temp_dict['role_category_id'] = i['role_category_id']
#         temp_dict['status'] = i['status']
#         temp_dict['created_at'] = i['created_at'].strftime('%Y-%m-%d %I:%M %p')
#         temp_list.append(temp_dict)

#     temp_list2 = []
#     for i2 in profile2:
#         userData2 = Users.objects.filter(id = i2['user_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         hustlerData2 = Users.objects.filter(id = i2['hustler_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')
#         temp_dict2 = {}
#         temp_dict2['id'] = i2['id']
#         temp_dict2['user_id'] = i2['user_id']
#         temp_dict2['hustler_id'] = i2['hustler_id']
#         temp_dict2['user_data'] = userData2[0]
#         temp_dict2['notification'] = i2['notification']
#         temp_dict2['seeker_notification'] = i2['seeker_notification']
#         temp_dict2['notifica_type'] = i2['notifica_type']
#         temp_dict2['status'] = i2['status']
#         temp_dict2['created_at'] = i2['created_at'].strftime('%Y-%m-%d %I:%M %p')
#         temp_list2.append(temp_dict2) 
   
#     return Response({'status': 200, 'message': 'Notifications', 'hustlers': temp_list2, 'seekers': temp_list}) 

# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def update_connect_status(request):
#     data = request.data
    

#     if Notifications.objects.filter(id=data['notification_id']).exists():
#         noti_obj = Notifications.objects.filter(id = data['notification_id'])[0]
#         noti_obj.status = data['status']
#         noti_obj.save()
        
#         userData = Users.objects.filter(id=noti_obj.user_id).values('device_token').first()
#         hustlerData = Users.objects.filter(id=noti_obj.hustler_id).values('device_token').first()

#         url = "https://fcm.googleapis.com/fcm/send"
#         if userData and hustlerData:
#             # Define the data to be sent in the notification
#             dataa = {
#                 "to": userData['device_token'],
#                 "notification": {
#                     "body": 'Your request is '+data['status'],
#                     "priority": "high",
#                     "title": 'Your request is '+data['status'],
#                     "message_id": data['notification_id'],
#                     "sound": "app_sound.wav",
#                 },
#                 "data": {
#                     "priority": "high",
#                     "title": 'Your request is '+data['status'],
#                     "body": 'Your request is '+data['status'],
#                     "message_id": data['notification_id'],
#                     "sound": "app_sound.wav",
#                     "content_available": True
#                 }
#             }

#             # Convert the data dictionary to a JSON string
#             payload = json.dumps(dataa)

#             # Define the headers
#             headers = {
#                 'Authorization': 'key=AAAAMmfUttw:APA91bFl7CTYHRar2M4KAY_GskDEfApLqawNehtyL7_vjNWsF476TAwT1a3Rf5PNkS2F9D6tTUzC8cShbvRYukWU5STpEkeiiIld0Yd8OnBQLL8heqfYfOeNqjCYJxnh_LNhCwmlx-4P',
#                 'Content-Type': 'application/json'
#             }

#             # Send the POST request with the payload and headers
#             response = requests.post(url, headers=headers, data=payload)  
#         else:
            
#             return Response({'status': 200, 'msg': 'Notification id not correct'})

        

#         if data['type'] == "connect":

#             if data['status'] == 'Accepted':
#                 conn_obj = Connect.objects.filter(id = noti_obj.connect_id)[0]
#                 conn_obj.status = 'Accepted'
#                 conn_obj.save()
#                 return Response({'status': 200, 'msg': 'Request Accepted'})
#             else:
#                 Notifications.objects.filter(id = data['notification_id']).delete()
#                 Connect.objects.filter(id = noti_obj.connect_id).delete()
#                 return Response({'status': 200, 'msg': 'Request Rejected'})
#         else:
            
#             if data['status'] == 'Accepted':
#                 conn_obj1 = Appointments.objects.filter(id = noti_obj.connect_id)[0]
#                 conn_obj1.status = 'Accepted'
#                 conn_obj1.save()
#                 return Response({'status': 200, 'msg': 'Request Accepted'})
#             else:
#                 # Notifications.objects.filter(id = data['notification_id']).delete()
#                 # Appointments.objects.filter(id = data['notification_id']).delete()
#                 # Connect.objects.filter(id = noti_obj.connect_id).delete()
#                 return Response({'status': 200, 'msg': 'Request Rejected'})

              
#     else:
        
#         return Response({'status': 400, 'msg': 'Notification id not correct.'})

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

# def send_notification(request):
#     url = "https://fcm.googleapis.com/fcm/send"

#     # Define the data to be sent in the notification
#     data = {
#         "to": "fW-Ubcj2TbKmfMy-GFeqIE:APA91bHmzVqYLHelGQHtTC_4iHrRlUxkqOe3YYU0vp_Xlm4UQS5VO26Fi_lAWrFpgj7zVIfPvnxk7o4LnX7tkYeuBmt833UaEkPBpxXLBWWRPePWfP5FcFi3ExeSgNyZa-LjbbFGC-md",
#         "notification": {
#             "body": "New announcement assigned",
#             "priority": "high",
#             "message_id": '1',
#             "title": "hello",
#             "sound": "app_sound.wav",
#         },
#         "data": {
#             "priority": "high",
#             "message_id": '1',
#             "title": "hello",
#             "body": "New announcement assignedaaaa",
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

#     # Return the response
#     return Response({'status':200,'msg':'sent'})

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


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def messages(request):
#     data = request.data    
#     messages_data = Chat.objects.filter(Q(sender_id=data['user_id']) | Q(receiver_id=data['user_id'])).values('id', 'category_id', 'category_name').distinct('category_name')
#     temp_list = []

#     for i in messages_data:
#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['user_id'] = data['user_id']  # Assuming user_id should be the same as in the request data
#         temp_dict['category_id'] = i['category_id']
#         temp_dict['category_name'] = i['category_name']
#         temp_dict['inbox'] = []

#         messagess = Chat.objects.filter(category_name=i['category_name']).filter(Q(sender_id=data['user_id']) | Q(receiver_id=data['user_id'])).values('id', 'sender_id', 'receiver_id', 'message', 'status', 'created_at').distinct('sender_id', 'receiver_id')
        
#         for messag in messagess:
#             if messag['sender_id'] == data['user_id']:
#                 userData = Users.objects.filter(id=messag['receiver_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')[0]
#             else:
#                 userData = Users.objects.filter(id=messag['sender_id']).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude')[0]
#             last_message = Chat.objects.filter(Q(sender_id=data['user_id']) | Q(receiver_id=data['user_id'])).values('id', 'message', 'status', 'created_at').order_by('-created_at').first()
#             temp_dict2 = {
#                 'id': messag['id'],
#                 'userData': userData,
#                 'message': last_message['message'],
#                 'status': last_message['status'],
#                 'created_at': messag['created_at'].strftime('%Y-%m-%d %I:%M %p')
#             }
#             temp_dict['inbox'].append(temp_dict2)
        
#         temp_list.append(temp_dict)

#     return Response({'status': 200, 'msg': 'Messages.', 'data': temp_list})


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @csrf_exempt
# def messages_list(request):
#     data = request.data    
#     messages_data = Chat.objects.filter((Q(sender_id=data['other_user_id']) & Q(receiver_id=data['user_id'])) | (Q(sender_id=data['user_id']) & Q(receiver_id=data['other_user_id']))).values('id', 'category_id', 'category_name', 'sender_id', 'receiver_id', 'message', 'status', 'created_at')
#     temp_list = []

#     for i in messages_data:

#         temp_dict = {}
#         temp_dict['id'] = i['id']
#         temp_dict['category_id'] = i['category_id']
#         temp_dict['category_name'] = i['category_name']
#         temp_dict['sender_id'] = i['sender_id']
#         temp_dict['receiver_id'] = i['receiver_id']
#         temp_dict['message'] = i['message']
#         temp_dict['status'] = i['status']
#         temp_dict['created_at'] = i['created_at'].strftime('%Y-%m-%d %I:%M %p')


#         temp_list.append(temp_dict)

#     return Response({'status': 200, 'msg': 'Messages.', 'data': temp_list})    