from django.urls import path
from . import views

app_name = 'eduroam'

urlpatterns = [
    path('', views.EduroamList.as_view(), name='list'),
    path('create/', views.EduroamCreate.as_view(), name='create'),
    path('<int:pk>/', views.EduroamDetail.as_view(), name='detail'),
    path('<int:pk>/update/', views.EduroamUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.EduroamDelete.as_view(), name='delete'),
]