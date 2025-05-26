from django.urls import path
from .views import create_category,update_category,role_category,Show_role_category,delete_category,top_profiles,messages_list, messages,connect,send_message,notifications,update_connect_status
#, ,Show_role_category,messages_list, messages, send_message, get_distance, add_post, Show_role_category, send_notification, get_hustler_slots, booking_appointment, 
# all_appointments, add_review, hustler_links, update_connect_status, notifications, top_reviews, update_category, , mini_resume, add_to_wallet, connect, top_videos

urlpatterns = [
    path('store/', create_category, name='create_category'),
    path('Show_role_category/', Show_role_category, name='Show_role_category'),
    path('role_category/', role_category, name='role_category'),
    path('update_category/', update_category, name='update_category'),
    path('top_profiles/', top_profiles, name='top_profiles'),
    # path('mini_resume/', mini_resume, name='mini_resume'),
    # path('add_to_wallet/', add_to_wallet, name='add_to_wallet'),
    path('connect/', connect, name='connect'),
    
    # path('top_videos/', top_videos, name='top_videos'),
    # path('add_review/', add_review, name='add_review'),
    # path('top_reviews/', top_reviews, name='top_reviews'),
    path('notifications/', notifications, name='notifications'),
    path('update_connect_status/', update_connect_status, name='update_connect_status'),
    # path('hustler_links/', hustler_links, name='hustler_links'),
    # path('booking_appointment/', booking_appointment, name='booking_appointment'),
    # path('all_appointments/', all_appointments, name='all_appointments'),
    # path('get_hustler_slots/', get_hustler_slots, name='get_hustler_slots'),
    # path('send_notification/', send_notification, name='send_notification'),
    path('delete_category/', delete_category, name='delete_category'),
    # path('add_post/', add_post, name='add_post'),
    # path('get_distance/', get_distance, name='get_distance'),
    path('send_message/', send_message, name='send_message'),
    path('messages/', messages, name='messages'),
    path('messages_list/', messages_list, name='messages_list'),
    
]

# urls.py
