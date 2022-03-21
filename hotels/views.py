from django.db.models import Q
from django.views.generic import ListView

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
        queryset = queryset.select_related('city', 'country').prefetch_related('reviews')
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
            if filter_arrival_date:
                queryset = queryset.filter(~Q(rooms__reservations__arrival_date__gte=filter_arrival_date))
            if filter_departure_date:
                queryset = queryset.filter(~Q(rooms__reservations__arrival_date__lte=filter_arrival_date))
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
