from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy, reverse
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)

from .forms import (HotelFilterForm, HotelForm,
                    RoomCreationForm, RoomFormset,
                    ReviewForm)
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
        self.getting_review_data(context, hotel, reviews)
        return context

    def getting_review_data(self, context, hotel, reviews):
        if self.request.user.is_authenticated:
            user = self.request.user
            is_reviewed = reviews.filter(reservation__user=user).exists()
            if not is_reviewed:
                reserves = Reservation.objects.filter(user=user, hotel=hotel)
                reserve = reserves.first()
                if reserves:
                    context['form'] = ReviewForm(initial={'reservation': reserve})

    def post(self, request, *args, **kwargs):
        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            Review.objects.create(**review_form.cleaned_data)
        return HttpResponseRedirect(
            reverse('hotels:hotel-detail', kwargs={'pk': self.get_object().pk})
        )

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


@permission_required('hotels.add_rooms')
def create_room(request, hotel_pk):
    hotel = get_object_or_404(Hotel, pk=hotel_pk)
    if request.method == 'POST':
        formset = RoomFormset(
            request.POST, request.FILES, instance=hotel
        )
        if formset.is_valid():
            formset.save()
    else:
        formset = RoomFormset(instance=hotel)
    return render(request,
                  'hotels/room_create.html',
                  {'formset': formset, 'hotel': hotel})


class RoomUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Room
    form_class = RoomCreationForm
    template_name = 'hotels/room_update.html'
    permission_required = 'hotels.change_rooms'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('hotel')
        return queryset
