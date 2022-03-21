from django.urls import path
from . import views


app_name = 'hotels'

urlpatterns = [
    path('', views.HotelListView.as_view(), name='hotels-list'),
    path('<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail')
]
