from django.contrib.auth.views import LogoutView, PasswordChangeView
from django.urls import path, reverse_lazy

from . import views
from .forms import CustomPasswordChangeForm

app_name = 'accounts'

urlpatterns = [
    path('sign-up/', views.SignUpView.as_view(), name='sign-up'),
    path('sign-in/', views.SignInView.as_view(), name='sign-in'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('dashboard/', views.UserDashboardView.as_view(), name='dashboard'),
    path('booking-list/', views.ReservationListView.as_view(), name='booking-list'),
    path('reviews-list/', views.ReviewListView.as_view(), name='reviews-list'),
    path('change-password/',
         PasswordChangeView.as_view(
             template_name='accounts/change_password.html',
             form_class=CustomPasswordChangeForm,
             success_url=reverse_lazy('accounts:profile')
         ),
         name='password_change'),
    path('password-reset/', views.CustomPasswordResetView.as_view(),
         name='password_reset'),
    path('password-reset-done/', views.CustomPasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('password/reset/<str:uidb64>/<str:token>', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset-complete/', views.CustomPasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
