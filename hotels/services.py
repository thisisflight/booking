import datetime

from django.db.models import Q, Count, Value, F
from django.db.models.functions import Coalesce


def processing_dates(context, previous_link, rooms):
    arrival_date, departure_date = getting_dates(context, previous_link)
    if all([arrival_date, departure_date]):
        reserved_rooms = rooms.filter(
            (
                    Q(reservations__arrival_date__gte=arrival_date) &
                    Q(reservations__arrival_date__lte=departure_date))
            | (
                    Q(reservations__departure_date__gte=arrival_date) &
                    Q(reservations__departure_date__lte=departure_date))
            | (
                    Q(reservations__arrival_date__lte=arrival_date) &
                    Q(reservations__departure_date__gte=departure_date))
        ).values_list('id')
        rooms_ids = dict.fromkeys(
            value[0] for value in
            rooms.filter(~Q(id__in=reserved_rooms)).values_list('id')
        )
        context['ids'] = rooms_ids
        context['rooms_amount'] = len(rooms_ids)


def getting_dates(context, previous_link):
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
    return arrival_date, departure_date


def processing_get_parameters(form, queryset):
    country = form.cleaned_data.get('country')
    arrival_date = form.cleaned_data.get('arrival_date')
    departure_date = form.cleaned_data.get('departure_date')
    min_price = form.cleaned_data.get('min_price')
    max_price = form.cleaned_data.get('max_price')
    capacity = form.cleaned_data.get('capacity')
    is_available = form.cleaned_data.get('is_available')
    stars_list = []
    five_star = form.cleaned_data.get('five_star_hotel')
    if five_star:
        stars_list.append(5)
    four_star = form.cleaned_data.get('four_star_hotel')
    if four_star:
        stars_list.append(4)
    three_star = form.cleaned_data.get('three_star_hotel')
    if three_star:
        stars_list.append(3)
    two_star = form.cleaned_data.get('two_star_hotel')
    if two_star:
        stars_list.append(2)
    one_star = form.cleaned_data.get('one_star_hotel')
    if one_star:
        stars_list.append(1)
    options = form.cleaned_data.get('options')
    if country:
        queryset = queryset.filter(country=country)
    if arrival_date and departure_date and is_available:
        queryset = queryset.annotate(
            total_rooms=Coalesce(Count('rooms', distinct=True), Value(0))
        )
        filter_reserved_rooms = (
         Q(rooms__reservations__arrival_date__gte=arrival_date) &
         Q(rooms__reservations__arrival_date__lte=departure_date)
                                ) | (
         Q(rooms__reservations__departure_date__gte=arrival_date) &
         Q(rooms__reservations__departure_date__lte=departure_date)
                                ) | (
         Q(rooms__reservations__arrival_date__lte=arrival_date) &
         Q(rooms__reservations__departure_date__gte=departure_date)
                                )
        queryset = queryset.annotate(reserved_rooms=Coalesce(Count(
            'rooms', distinct=True, filter=filter_reserved_rooms), Value(0)))
        queryset = queryset.annotate(
            free_rooms=F('total_rooms') - F('reserved_rooms')
        )
        queryset = queryset.filter(free_rooms__gt=0)
    if min_price:
        queryset = queryset.filter(rooms__price__gte=min_price)
    if max_price:
        queryset = queryset.filter(rooms__price__lte=max_price)
    if stars_list:
        queryset = queryset.filter(category__in=stars_list)
    if options:
        queryset = queryset.filter(options__in=options)
    if capacity:
        queryset = queryset.filter(rooms__capacity__gte=capacity)
    return queryset
