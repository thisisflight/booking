from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import (ListView, DetailView,
                                  CreateView, UpdateView, DeleteView)

from utils.form_dates import reconfigure_form_dates
from .forms import (HotelFilterForm, HotelForm,
                    RoomCreationForm, RoomFormset,
                    ReviewForm, ReservationForm)
from .models import Hotel, Review, Reservation, Room
from .services import (processing_dates,
                       processing_get_parameters)


class HotelListView(ListView):
    model = Hotel
    template_name = 'hotels/hotels_list.html'
    paginate_by = 6

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Список отелей'
        context['form'] = HotelFilterForm(self.request.GET)
        is_filter_used = bool(self.request.GET)
        if is_filter_used:
            query = '&'.join([value for item in self.request.GET.items()
                              if 'page' not in (value := '='.join(item))])
            context['query'] = query
        context['is_filter_used'] = is_filter_used
        context['hotels_amount'] = self.request.session.get('hotels_amount')
        return context

    def get(self, request, *args, **kwargs):
        self.request.GET._mutable = True
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('city', 'country')
        queryset = queryset.prefetch_related('reservations__reviews')
        queryset = queryset.with_cheapest_price_and_average_rate()
        form = HotelFilterForm(self.request.GET)
        if form.is_valid():
            queryset = processing_get_parameters(self.request, form, queryset)
        self.request.session['hotels_amount'] = str(len(queryset))
        self.request.session.modified = True
        return queryset


class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotels/hotel_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.object
        rooms = hotel.rooms.all()
        context['rooms'] = rooms
        arrival_date, departure_date = processing_dates(
            self.request, context, rooms)
        if all([arrival_date, departure_date]) :
            reservation_form = ReservationForm(
                initial={
                    'user': self.request.user,
                    'hotel': hotel,
                    'arrival_date': arrival_date,
                    'departure_date': departure_date
                }
            )
            context['reservation_form'] = reservation_form
        dates_form = HotelFilterForm(self.request.POST)
        context['dates_form'] = dates_form
        reviews = Review.objects.select_related('reservation__user').only(
            "reservation__user__first_name",
            "reservation__user__last_name",
            "rate",
            "created"
        )
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
        request.POST._mutable = True
        review_form = ReviewForm(request.POST)
        reservation_form = ReservationForm(request.POST)
        if 'review' in request.POST:
            if review_form.is_valid():
                Review.objects.create(**review_form.cleaned_data)
        elif 'reserve' in request.POST:
            if reservation_form.is_valid():
                Reservation.objects.create(**reservation_form.cleaned_data)
                messages.success(request, 'Вы успешно забронировали номер')
                return HttpResponseRedirect(
                    reverse('accounts:booking-list')
                )
            else:
                login_url = reverse("accounts:sign-in")
                self_object_page_url = reverse(
                    'hotels:hotel-detail', kwargs={'pk': self.get_object().pk}
                )
                return HttpResponseRedirect(f"{login_url}?next={self_object_page_url}")
        elif 'dates' in request.POST:
            arrival_date = request.POST.get('arrival_date')
            departure_date = request.POST.get('departure_date')
            arrival_date, departure_date = (
                reconfigure_form_dates(
                    request.POST,
                    arrival_date, departure_date))
            request.session['arrival_date'] = arrival_date
            request.session['departure_date'] = departure_date
        request.POST._mutable = False
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
    permission_required = 'hotels.add_hotel'

    def get_success_url(self):
        messages.success(self.request, 'Отель успешно создан, время создать номера')
        return reverse('hotels:create-room', kwargs={'hotel_pk': self.object.id})


class HotelUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Hotel
    form_class = HotelForm
    template_name = 'hotels/hotel_update.html'
    permission_required = 'hotels.change_hotel'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        rooms = self.object.rooms.all()
        context['rooms'] = rooms
        return context


class DeleteReservationView(LoginRequiredMixin, DeleteView):
    model = Reservation
    template_name = 'accounts/booking_list.html'

    def get_success_url(self):
        messages.success(self.request, f'Бронирование успешно удалено')
        return reverse('accounts:booking-list')


@permission_required('hotels.add_room')
def create_room(request, hotel_pk):
    hotel = get_object_or_404(Hotel, pk=hotel_pk)
    if request.method == 'POST':
        formset = RoomFormset(
            request.POST, request.FILES, instance=hotel
        )
        if formset.is_valid():
            formset.save()
            messages.success(
                request,
                f'Номера успешно добавлены к отелю {hotel.name}')
            return HttpResponseRedirect(
                reverse('hotels:update-hotel',
                        kwargs={'pk': hotel_pk})
            )
    else:
        formset = RoomFormset(instance=hotel)
    return render(request,
                  'hotels/room_create.html',
                  {'formset': formset, 'hotel': hotel})


class RoomUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Room
    form_class = RoomCreationForm
    template_name = 'hotels/room_update.html'
    permission_required = 'hotels.change_room'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('hotel')
        return queryset
