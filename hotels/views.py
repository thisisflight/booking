import re

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)
from .forms import HotelFilterForm, HotelForm, RoomUpdateForm, RoomCreateForm
from .models import Hotel, Review, Reservation, Room
from .services import processing_dates, processing_get_parameters


class HotelListView(ListView):
    model = Hotel
    template_name = 'hotels/hotels_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Список отелей'
        context['form'] = HotelFilterForm(self.request.GET)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('city', 'country')
        queryset = queryset.prefetch_related('reservations__reviews')
        queryset = queryset.with_cheapest_price_and_average_rate()
        form = HotelFilterForm(self.request.GET)
        if form.is_valid():
            queryset = processing_get_parameters(form, queryset)
        return queryset.order_by('-pk')


class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotels/hotel_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_link = self.request.META.get('HTTP_REFERER')
        hotel = self.object
        rooms = hotel.rooms.all()
        context['rooms'] = rooms
        if previous_link and len(previous_link.split('?')) > 1:
            processing_dates(context, previous_link, rooms)
        reviews = Review.objects.select_related('reservation__user')
        reviews = reviews.filter(reservation__hotel=hotel)
        context['title'] = "Бронирование отеля"
        context['options'] = hotel.options.all()
        context['reviews'] = reviews
        context['reviews_amount'] = len(reviews)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('country', 'city')
        queryset = queryset.prefetch_related('options', 'rooms', 'reservations__reviews')
        queryset = queryset.with_cheapest_price_and_average_rate()
        return queryset


class HotelCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Hotel
    form_class = HotelForm
    template_name = 'hotels/hotel_update.html'
    success_url = reverse_lazy('accounts:dashboard')
    permission_required = 'hotels.add_hotels'


class HotelUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Hotel
    form_class = HotelForm
    template_name = 'hotels/hotel_update.html'
    permission_required = 'hotels.change_hotels'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = self.object.rooms.all()
        context['rooms'] = rooms
        return context


class DeleteReservationView(DeleteView):
    model = Reservation
    template_name = 'accounts/booking_list.html'
    success_url = reverse_lazy('accounts:booking-list')


class RoomCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Room
    template_name = 'hotels/room_create.html'
    form_class = RoomCreateForm
    permission_required = 'hotels.add_rooms'

    def get(self, request, *args, **kwargs):
        previous_link = request.META.get('HTTP_REFERER')
        if previous_link and '/hotels/update-hotel/' in previous_link:
            return super().get(request, *args, **kwargs)
        return redirect('main:index')

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('hotel')
        return queryset

    def get_success_url(self):
        return self.object.hotel.get_update_url()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_link = self.request.META.get('HTTP_REFERER')
        pk = re.findall(r'\d+', previous_link)[-1]
        hotel = Hotel.objects.get(pk=pk)
        context['hotel'] = hotel
        return context


class RoomUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Room
    form_class = RoomUpdateForm
    template_name = 'hotels/room_update.html'
    permission_required = 'hotels.change_rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('hotel')
        return queryset
