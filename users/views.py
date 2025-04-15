import string
import traceback
from django.conf import settings
from django.shortcuts import redirect, render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer
from .serializers import UpdateUserSerializer
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist
import random
from .models import Users
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from .serializers import ChangePasswordSerializer
from django.db import IntegrityError
from django.contrib import messages
from rest_framework.authentication import TokenAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        email = request.data.get('email')
        username = request.data.get('username')
        if Users.objects.filter(email=email).exists():
            # Return a response indicating that the email is already taken
            return Response({"error": {"error_code": 400, "error": "Email already exists"}}, status=status.HTTP_400_BAD_REQUEST)
        if Users.objects.filter(email=email).exists():
            # Return a response indicating that the email is already taken
            return Response({"error": {"error_code": 400, "error": "Username already exists"}}, status=status.HTTP_400_BAD_REQUEST)    
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error":{"error_code": 400,"error": serializer.errors}}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def Update_Profile(request):
    user_instance = request.user

    serializer = UpdateUserSerializer(instance=user_instance, data=request.data, partial=True)
    
    if serializer.is_valid():
        new_username = serializer.validated_data.get('username')
        if new_username and user_exists(new_username, user_instance):
            return Response({
                "error": {
                    "error_code": 400,
                    "error": {
                        "username": ["A user with that username already exists."]
                    }
                }
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({
            "success": {
                "code": 200,
                "base_url": 'https://hustlersandseekers.co/hustler/media/',
                "data": serializer.data
            }
        }, status=status.HTTP_200_OK)

    return Response({
        "error": {
            "error_code": 400,
            "error": serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)

def user_exists(username, current_user):
    # Check if any other user has the same username
    return Users.objects.exclude(id=current_user.id).filter(username=username).exists()


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.models import Token
from django.db.models import Q
from .models import Users  # Adjust if needed

@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')  # Can be email, username, or mobile
        password = request.data.get('password')
        device_token = request.data.get('device_token', '')
        latitude = request.data.get('latitude', '')
        longitude = request.data.get('longitude', '')

        user = None

        # Try login by email
        if '@' in username:
            try:
                user = Users.objects.get(email=username)
                if not user.check_password(password):
                    return Response({"error": {"error_code": 400, "error": "Invalid credentials"}}, status=status.HTTP_401_UNAUTHORIZED)
            except ObjectDoesNotExist:
                user = None

        # Fallback to Django authentication
        if not user:
            user = authenticate(username=username, password=password)

        if user:
            # Update device token and location
            user_obj = Users.objects.filter(Q(email=username) | Q(username=username)).first()
            if user_obj:
                user_obj.device_token = device_token
                user_obj.latitude = latitude
                user_obj.longitude = longitude
                user_obj.save()

            # Reset token
            Token.objects.filter(user=user).delete()
            token = Token.objects.create(user=user)

            # Keep the response data as you originally had
            profile = Users.objects.filter(Q(email=username) | Q(username=username)).values('id', 'username', 'email','radius_km').first()

            return Response({'token': token.key, 'data': profile}, status=status.HTTP_200_OK)

        return Response({"error": {"error_code": 400, "error": "Invalid credentials"}}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    if request.method == 'POST':
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.data.get('old_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                update_session_auth_hash(request, user)  # To update session after password change
                return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
            return Response({'error': 'Incorrect old password.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)      

 
@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@authentication_classes([TokenAuthentication])
@csrf_exempt
def Show_User_Profile(request):
    try:
        data = request.data
        
        if Users.objects.filter(id = data.get('user_id'),is_staff = False).exists():
            profile = Users.objects.filter(id = data.get('user_id')).values('id', 'username', 'email', 'phone', 'image', 'gender', 'dob', 'first_name', 'last_name', 'location', 'banner_image', 'latitude', 'longitude','radius_km')
            return Response({'status':200,'msg':'User Profile.', 'base_url': 'https://hustlersandseekers.co/hustler/media/','payload':profile[0]})
        else:
            return Response({'status':403,'msg':'Invalid User.'})
    except:
        return Response({'status':403,'msg':'Something went wrong.'})  
        
       
@api_view(['POST'])
@csrf_exempt
def Forgot_Password(request):
    data = request.data
    if Users.objects.filter(email = data['email']).exists():
        letters = string.ascii_lowercase + '0123456789'
        password = ''.join(random.choice(letters) for i in range(6))
        user = Users.objects.filter(email = data['email'])[0]
        user.reset_code = password
        user.save()
        send_mail('Forgot Password', f'Hi {user.username} \nYour password is: {password}.Please Do not share your login credentials with anyone.\nTeam hustlersandseekers', settings.EMAIL_HOST_USER, [data['email']])
        return Response({'status':200, 'code':password, 'msg':'Password sent on your registered email address.'})
    else:
        return Response({'status':400,'msg':'Invalid User.'})  

@api_view(['POST'])
@csrf_exempt
def reset_password(request):
    data = request.data
    if Users.objects.filter(email = data['email'], reset_code = data['code']).exists():
        password = data['new_password']
        user = Users.objects.filter(email=data['email'])[0]
        user.set_password(password)
        user.save()
        return Response({'status':200, 'msg':'Password reset successfully.'})
    else:
        return Response({'status':400,'msg':'Invalid Code with this user.'})  
