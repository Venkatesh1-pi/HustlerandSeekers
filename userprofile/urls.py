from django.urls import path
from .views import ViewProfile, UpdateProfile

urlpatterns = [
    path('view/', ViewProfile.as_view(), name='view-profile'),
    path('update/', UpdateProfile.as_view(), name='update-profile'),
]
