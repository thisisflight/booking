import datetime
from collections import Counter

from allauth.account.views import LoginView
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.contrib.auth.models import User, Group
from django.contrib.auth.views import (PasswordResetView,
                                       PasswordResetDoneView,
                                       PasswordResetConfirmView,
                                       PasswordResetCompleteView)
from django.db.models import F, ExpressionWrapper, DurationField
from django.db.models.functions import Coalesce
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (UpdateView, TemplateView,
                                  ListView, CreateView)

from hotels.models import Reservation, Review, Hotel
from .forms import (ChangeProfileInfoForm, CustomUserCreationForm,
                    CustomAuthenticationForm, CustomPasswordResetForm,
                    CustomSetPasswordForm)
from .models import Profile


class CheckCustomerMixin:

    def check_if_user_is_admin(self):
        return self.request.user.groups.filter(
            name__exact='Администратор'
        ).exists()

    def check_if_user_is_customer(self):
        return self.request.user.groups.filter(
            name__exact='Пользователь'
        )

    def check_if_user_is_not_customer(self):
        return self.request.user.groups.filter(
            name__in=['Администратор', 'Контент-менеджер']
        ).exists()


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
        login(
            self.request, user=user,
            backend="django.contrib.auth.backends.ModelBackend")
        messages.success(self.request,
                         f'Вы зашли как пользователь '
                         f'{self.request.user.username}')
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


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/forgot_password.html'
    form_class = CustomPasswordResetForm
    email_template_name = 'accounts/password_reset_email.txt'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('accounts:password_reset_done')
    html_email_template_name = 'accounts/password_reset_email.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Восстановление пароля'
        return context

    def form_valid(self, form):
        self.request.session['reset_email'] = form.cleaned_data['email']
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/forgot_password_done.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reset_email'] = self.request.session.get('reset_email', '')
        context['title'] = 'Восстановление пароля'
        return context


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    form_class = CustomSetPasswordForm
    success_url = reverse_lazy('accounts:password_reset_complete')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Установка нового пароля'
        return context


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


class UserProfileView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'accounts/profile.html'
    form_class = ChangeProfileInfoForm
    success_url = reverse_lazy('accounts:profile')

    def get_object(self, queryset=None):
        print(self.request.user.groups)
        return self.request.user.profile

    def form_valid(self, form):
        user = self.request.user
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')
        role = form.cleaned_data.get('role')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        if username:
            user.username = username
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if role:
            group = Group.objects.get(name__exact=role)
            user.groups.clear()
            group.user_set.add(user)
        if any([username, email, first_name, last_name]):
            user.save()
        messages.success(self.request, 'Вы успешно обновили профиль')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request,
                       'Поправьте некорректные данные и нажмите Сохранить')
        return super().form_invalid(form)


class UserDashboardView(LoginRequiredMixin, PermissionRequiredMixin,
                        CheckCustomerMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    permission_required = 'hotels.add_hotel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.check_if_user_is_admin():
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


class ReservationListView(LoginRequiredMixin, CheckCustomerMixin, ListView):
    model = Reservation
    template_name = 'accounts/booking_list.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'hotel__city', 'hotel__country', 'room', 'user'
        )
        queryset = queryset.prefetch_related('reviews')
        queryset = queryset.annotate(
            rate=Coalesce('reviews__rate', 0)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        if self.check_if_user_is_customer():
            context['is_customer'] = True
            queryset = queryset.filter(user=self.request.user)
            queryset = queryset.annotate(
                deny=ExpressionWrapper(
                    F('departure_date') - datetime.date.today(),
                    output_field=DurationField()
                )
            )
        reservations_with_rates = Counter()
        for item in queryset:
            reservations_with_rates[item.hotel.id] += item.rate
        context["reservations_dict"] = dict(reservations_with_rates)
        context['reservations'] = queryset
        return context


class ReviewListView(LoginRequiredMixin, CheckCustomerMixin, ListView):
    model = Review
    template_name = 'accounts/review_list.html'
    context_object_name = 'reviews'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related(
            'reservation__hotel__country',
            'reservation__hotel__city'
        )
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
        if self.check_if_user_is_customer():
            queryset = self.get_queryset().filter(reservation__user=self.request.user)
            context['reviews'] = queryset
        return context
