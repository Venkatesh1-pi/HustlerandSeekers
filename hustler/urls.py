from django.contrib import admin

from django.urls import path, include

from django.contrib.staticfiles.urls import staticfiles_urlpatterns



urlpatterns = [

    path('djadmin', admin.site.urls),

   

    # path('admin/',include('dashboard.urls')),

    path('api/', include('users.urls')),
     path('news/', include('news.urls')),


    # path('api/role_category/', include('hustler_role_category.urls')),

    # path('api/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),

    
]

urlpatterns += staticfiles_urlpatterns()
