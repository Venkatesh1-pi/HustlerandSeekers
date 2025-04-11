from django.urls import path
from .views import get_news_data

urlpatterns = [
    path('get-news/', get_news_data, name='get-news'),
]
