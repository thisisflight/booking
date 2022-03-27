from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView


app_name = 'accounts'

urlpatterns = [
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('sign-in/', views.SignInView.as_view(), name='sign-in'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('booking-list/', views.ReservationListView.as_view(), name='booking-list'),
    path('reviews-list/', views.ReviewListView.as_view(), name='reviews-list')
]
