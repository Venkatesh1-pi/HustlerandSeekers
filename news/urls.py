from django.urls import path
from .views import get_news_data
from django.urls import path
from .views import get_news_categories



urlpatterns = [
    path('get-news/', get_news_data, name='get-news'),
    path('categories/', get_news_categories, name='news-categories'),
]
