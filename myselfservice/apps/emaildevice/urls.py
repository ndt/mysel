from django.urls import path
from . import views

app_name = 'emaildevice'

urlpatterns = [
    path('', views.EmailDeviceList.as_view(), name='list'),
    path('create/', views.EmailDeviceCreate.as_view(), name='create'),
    path('<int:pk>/update/', views.EmailDeviceUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.EmailDeviceDelete.as_view(), name='delete'),
]