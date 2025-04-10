import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User
from .serializers import RegisterSerializer, LoginSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

reset_code_store = {}  # In-memory store for demo

from rest_framework.permissions import AllowAny

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registration successful"}, status=201)
        return Response(serializer.errors, status=400)

from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication 

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(request, username=serializer.validated_data['username'], password=serializer.validated_data['password'])

            if user:
                refresh = RefreshToken.for_user(user)
                return Response({
                    "message": "Login successful",
                    "token": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                })
        return Response({"error": "Invalid credentials"}, status=400)


class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            if User.objects.filter(email=email).exists():
                code = str(random.randint(100000, 999999))
                reset_code_store[email] = code
                send_mail(
                    'Reset Your Password',
                    f'Use this code to reset your password: {code}',
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                return Response({"message": "Reset code sent to email"})
            return Response({"error": "User with this email does not exist"}, status=404)
        return Response(serializer.errors, status=400)

class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']
            confirm_password = serializer.validated_data['confirm_password']
            email = next((k for k, v in reset_code_store.items() if v == code), None)

            if not email:
                return Response({"error": "Invalid code"}, status=400)
            if new_password != confirm_password:
                return Response({"error": "Passwords do not match"}, status=400)

            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()
            del reset_code_store[email]
            return Response({"message": "Password reset successful"})
        return Response(serializer.errors, status=400)
