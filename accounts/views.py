from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, TemplateView, ListView, CreateView

from hotels.models import Reservation, Review, Hotel
from .forms import (ChangeProfileInfoForm, CustomUserCreationForm,
                    CustomAuthenticationForm)
from .models import Profile


class SignUpView(CreateView):
    model = User
    template_name = 'accounts/sign_up.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('main:index')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        result = super().form_valid(form)
        username = form.cleaned_data['username']
        email = form.cleaned_data.get('email')
        user = User.objects.get(username=username)
        user.email = email
        user.save()
        login(self.request, user=user)
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание аккаунта'
        return context


class SignInView(LoginView):
    form_class = CustomAuthenticationForm
    template_name = 'accounts/sign_in.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('main:index')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Вход'
        return context


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'accounts/profile.html'
    form_class = ChangeProfileInfoForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        user = self.request.user
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        role = form.cleaned_data.get('role')
        if username:
            user.username = username
        if email:
            user.email = email
        if role:
            group = Group.objects.get(name__exact=role)
            user.groups.clear()
            group.user_set.add(user)
        if any([username, email]):
            user.save()
        return super().form_valid(form)


class UserDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_role = self.request.user.profile.role.name
        if user_role != 'Пользователь':
            context['is_not_customer'] = True
        else:
            context['is_not_customer'] = False
        if user_role == 'Администратор':
            users_amount = User.objects.all().count()
            reservations_amount = Reservation.objects.count()
            reviews_count = Review.objects.count()
            context['users_amount'] = users_amount
            context['reservations_amount'] = reservations_amount
            context['reviews_count'] = reviews_count
            context['is_admin'] = True
        hotels = Hotel.objects.select_related('city', 'country')
        hotels = hotels.with_all_reservations_and_views()
        hotels = hotels.only('country__name', 'city__name', 'name')
        context['hotels'] = hotels
        return context


class ReservationListView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'accounts/booking_list.html'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('hotel', 'room')
        queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_context_value(self, context)
        return context


class ReviewListView(LoginRequiredMixin, ListView):
    model = Review
    template_name = 'accounts/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'reservation__hotel__country',
            'reservation__hotel__city'
        )
        queryset = queryset.filter(reservation__user=self.request.user)
        queryset = queryset.only(
            'reservation__hotel__name',
            'reservation__hotel__category',
            'reservation__hotel__city__name',
            'reservation__hotel__country__name',
            'reservation__arrival_date',
            'reservation__departure_date',
            'rate',
            'text'
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        get_context_value(self, context)
        return context


def get_context_value(self, context):
    user_role = self.request.user.profile.role.name
    if user_role != 'Пользователь':
        context['is_not_customer'] = True
    else:
        context['is_not_customer'] = False
