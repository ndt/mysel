# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.core.urls')),
    path('guests/', include('apps.guests.urls')),
    path('eduroam/', include('apps.eduroam.urls')),
    path('events/', include('apps.events.urls')),
    path('emaildevice/', include('apps.emaildevice.urls')),
]