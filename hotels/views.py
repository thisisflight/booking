import datetime

from django.db.models import Q, Max
from django.views.generic import ListView, DetailView

from .forms import HotelFilterForm
from .models import Hotel


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
        queryset = queryset.prefetch_related('reviews')
        queryset = queryset.with_cheapest_price_and_average_rate()
        form = HotelFilterForm(self.request.GET)
        if form.is_valid():
            filter_country = form.cleaned_data.get('country')
            filter_arrival_date = form.cleaned_data.get('arrival_date')
            filter_departure_date = form.cleaned_data.get('departure_date')
            filter_min_price = form.cleaned_data.get('min_price')
            filter_max_price = form.cleaned_data.get('max_price')
            filter_capacity = form.cleaned_data.get('capacity')
            stars_list = []
            filter_five_star = form.cleaned_data.get('five_star_hotel')
            if filter_five_star:
                stars_list.append(5)
            filter_four_star = form.cleaned_data.get('four_star_hotel')
            if filter_four_star:
                stars_list.append(4)
            filter_three_star = form.cleaned_data.get('three_star_hotel')
            if filter_three_star:
                stars_list.append(3)
            filter_two_star = form.cleaned_data.get('two_star_hotel')
            if filter_two_star:
                stars_list.append(2)
            filter_one_star = form.cleaned_data.get('one_star_hotel')
            if filter_one_star:
                stars_list.append(1)
            filter_options = form.cleaned_data.get('options')
            if filter_country:
                queryset = queryset.filter(country=filter_country)
            if filter_arrival_date and filter_departure_date:
                max_date = queryset.aggregate(
                    max_date=Max('reservations__departure_date')
                ).get('max_date')
                queryset = queryset.filter(
                    (Q(reservations__arrival_date__lte=filter_arrival_date) &
                     Q(reservations__departure_date__gte=filter_arrival_date)) |
                    Q(reservations__departure_date__lte=max_date)
                )
            if filter_min_price:
                queryset = queryset.filter(rooms__price__gte=filter_min_price)
            if filter_max_price:
                queryset = queryset.filter(rooms__price__lte=filter_max_price)
            if stars_list:
                queryset = queryset.filter(category__in=stars_list)
            if filter_options:
                queryset = queryset.filter(options__in=filter_options)
            if filter_capacity:
                queryset = queryset.filter(rooms__capacity__gte=filter_capacity)
        return queryset.order_by('-pk')


class HotelDetailView(DetailView):
    model = Hotel
    template_name = 'hotels/hotel_booking.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        previous_link = self.request.META.get('HTTP_REFERER')
        rooms = self.object.rooms.all()
        context['rooms'] = rooms
        if previous_link and len(previous_link.split('?')) > 1:
            request_data = dict([item.split('=')
                                 for item in previous_link.split('?')[1].split('&')])
            arrival_date = request_data.get('arrival_date')
            if arrival_date:
                arrival_date = datetime.datetime.strptime(arrival_date, '%Y-%m-%d')
            departure_date = request_data.get('departure_date')
            if departure_date:
                departure_date = datetime.datetime.strptime(departure_date, '%Y-%m-%d')
            context['arrival_date'] = arrival_date
            context['departure_date'] = departure_date
            if all([arrival_date, departure_date]):
                reserved_rooms = self.object.rooms.filter(
                    reservations__arrival_date__lte=arrival_date,
                    reservations__departure_date__gte=arrival_date
                ).values_list('id')
                rooms_ids = {value[0]: None for value in reserved_rooms}
                context['ids'] = rooms_ids
                context['rooms_amount'] = len(rooms)
        reviews = self.object.reviews.select_related('user__profile').order_by('-pk')
        context['title'] = "Бронирование отеля"
        context['options'] = self.object.options.all()
        context['reviews'] = reviews
        context['reviews_amount'] = len(reviews)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('country', 'city')
        queryset = queryset.prefetch_related('options', 'rooms', 'reviews')
        queryset = queryset.with_cheapest_price_and_average_rate()
        return queryset
