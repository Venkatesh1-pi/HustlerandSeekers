import concurrent.futures
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
import xmltodict
import numpy as np
from geopy.distance import distance


def fetch_google_news_rss(search_query, city, area):
    search_query = f"{search_query}+{area}+{city}"
    
    url = f"https://news.google.com/rss/search?q={search_query}"
    #print(url)
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response
        else:
            return None
    except requests.RequestException as e:
        print(f"Error fetching Google News RSS: {e}")
        return None



import xmltodict
from bs4 import BeautifulSoup

def parse_news_data(news):
    data_dict = xmltodict.parse(news.content)
    news_items = data_dict['rss']['channel']['item']
    news_list = []

    for item in news_items:
        title = item['title']
        link = item['link']
        pub_date = item['pubDate']
        
        # Extract description
        description = item.get('description', '')
        
        # Check if description is HTML and convert to plain text if so
        if description:
            soup = BeautifulSoup(description, "html.parser")
            description_text = soup.get_text()  # Extract plain text from HTML
        else:
            description_text = description

        # Extract source (if available)
        source = item.get('source', '')

        news_list.append({
            'title': title,
            'link': link,
            'pubDate': pub_date,
            'description': description_text,
            'source': source
        })

    return news_list


# Function to reverse geocode and get city and area
def reverse_geocode(api_key, lat, lng):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        geocode_data = response.json()
        if geocode_data['results']:
            address_components = geocode_data['results'][0]['address_components']
            city = None
            area = None
            for component in address_components:
                if "locality" in component['types']:
                    city = component['long_name']
                if "sublocality" in component['types'] or "neighborhood" in component['types']:
                    area = component['long_name']
            if city and area:
                return city, area
    return None, None

# Function to get current location if lat and long are not provided
def get_current_location(api_key):
    url = 'https://www.googleapis.com/geolocation/v1/geolocate'
    params = {'key': api_key}
    response = requests.post(url, json={}, params=params)
    if response.status_code == 200:
        location_data = response.json()
        lat = location_data['location']['lat']
        lng = location_data['location']['lng']
        return lat, lng
    return None, None

# Function to generate multiple lat-long points in a given radius
def generate_coordinates(lat, lon, radius_km, step_km=8):
    coordinates = []
    for bearing in range(0, 360, 30):
        for step in np.arange(0, radius_km, step_km):
            new_point = distance(kilometers=step).destination((lat, lon), bearing)
            coordinates.append((new_point.latitude, new_point.longitude))
    return coordinates

# Helper function for processing a single lat-long point in parallel
def process_point(search_query,point, api_key):
    city, area = reverse_geocode(api_key, point[0], point[1])
    if city and area:
        try:
            news = fetch_google_news_rss(search_query,city, area)
            return parse_news_data(news)
        except Exception:
            return []
    return []
import json
import concurrent.futures
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

#from .utils import get_current_location, generate_coordinates, process_point  # assuming these are in utils.py

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
import concurrent.futures

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import concurrent.futures
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import concurrent.futures
import math

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse
import math
import concurrent.futures

# Store all news globally (or use cache/db for production)
all_news_data = []

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_news_data(request):
    print("View hit!")

    api_key = 'AIzaSyBoOL3y7PeYodAMDx8xuXeFN_WIwPVkJbw'

    body = request.data
    search_query = body.get('search_query')
    lat = body.get('latitude', '')
    lng = body.get('longitude', '')
    radius_km = body.get('radius_km', 25)
    page = int(body.get('page', 1))
    page_size = 10  # Fixed page size

    print(f"Search query: {search_query}")

    if not lat or not lng:
        lat, lng = get_current_location(api_key)
        print(lat, lng)
        if not lat or not lng:
            return JsonResponse({'error': 'Could not retrieve current location'}, status=400)

    try:
        lat = float(lat)
        lng = float(lng)
        radius_km = float(radius_km)
    except ValueError:
        return JsonResponse({'error': 'Invalid coordinates or radius'}, status=400)

    lat_long_points = generate_coordinates(lat, lng, radius_km=radius_km)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(lambda point: process_point(search_query, point, api_key), lat_long_points))

    news_data = [item for sublist in results for item in sublist]

    # Assign unique ID to each news item
    for idx, item in enumerate(news_data):
        item['id'] = idx

    # Save all for lookup in detail view
    global all_news_data
    all_news_data = news_data

    # Pagination
    total_items = len(news_data)
    total_pages = math.ceil(total_items / page_size)

    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = news_data[start_index:end_index]

    return JsonResponse({
        'news': paginated_data,
        'total_items': total_items,
        'total_pages': total_pages,
        'current_page': page
    }, status=200)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_single_news_detail(request):
    """
    Request Body: { "id": 2 }
    Response: Single news item with the same fields
    """
    news_id = request.data.get("id")

    if news_id is None:
        return JsonResponse({"error": "Missing 'id' in request body"}, status=400)

    try:
        news_id = int(news_id)
    except ValueError:
        return JsonResponse({"error": "Invalid 'id', must be an integer"}, status=400)
    print(news_id)
    global all_news_data

    print(all_news_data)

    return JsonResponse({"news": all_news_data[news_id]}, status=200)
    



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_news_categories(request):
    categories = [
        {'id': 1, 'category': 'finance'},
        {'id': 2, 'category': 'business'}
    ]
    return Response({'categories': categories}, status=status.HTTP_200_OK)

