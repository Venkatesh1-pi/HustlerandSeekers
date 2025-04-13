from django.urls import path
from .views import register_user, user_login, user_logout, change_password, reset_password, Show_User_Profile, Update_Profile, Forgot_Password

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('change_password/', change_password, name='change_password'),
    path('reset_password/', reset_password, name='reset_password'),
    path('Show_User_Profile/', Show_User_Profile, name='Show_User_Profile'),
    path('Update_Profile/', Update_Profile, name='Update_Profile'),
    path('Forgot_Password/', Forgot_Password, name='Forgot_Password'),
    
]
