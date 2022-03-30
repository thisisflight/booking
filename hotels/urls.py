from django.urls import path
from django.views.decorators.http import require_POST

from . import views

app_name = 'hotels'

urlpatterns = [
    path('', views.HotelListView.as_view(), name='hotels-list'),
    path('<int:pk>/', views.HotelDetailView.as_view(), name='hotel-detail'),
    path('create-hotel/', views.HotelCreateView.as_view(), name='create-hotel'),
    path('create-room/<int:hotel_pk>/', views.create_room, name='create-room'),
    path('update-room/<int:pk>/', views.RoomUpdateView.as_view(), name='update-room'),
    path('update-hotel/<int:pk>/', views.HotelUpdateView.as_view(), name='update-hotel'),
    path('delete-reservation/<int:pk>/',
         require_POST(views.DeleteReservationView.as_view()), name='delete-reservation'),
]
