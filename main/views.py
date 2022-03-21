from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from hotels.forms import HotelFilterForm
from hotels.models import Country, Hotel, Review


class MainPage(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        arrival_date = request.GET.get('arrival_date')
        departure_date = request.GET.get('departure_date')
        capacity = request.GET.get('capacity')
        link = reverse_lazy('hotels:hotels-list')
        if request.GET.get('search', '') == '1' and arrival_date:
            return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}")
        elif request.GET.get('search', '') == '1' and capacity:
            return HttpResponseRedirect(f"{link}?capacity={capacity}")
        elif request.GET.get('search', '') == '1' and arrival_date and departure_date:
            return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}"
                                        f"&departure_date={departure_date}")
        elif request.GET.get('search', '') == '1' and arrival_date and departure_date and capacity:
            return HttpResponseRedirect(f"{link}?arrival_date={arrival_date}"
                                        f"&departure_date={departure_date}"
                                        f"&capacity={capacity}")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = Country.objects.with_cheapest_price()
        hotels = Hotel.objects.select_related('city').prefetch_related('reviews')
        hotels = hotels.with_cheapest_price_and_average_rate().order_by('min_price')[:3]
        reviews = Review.objects.select_related('user__profile', 'hotel').all().order_by('-pk')[:3]
        context['flag'] = True
        context['main'] = True
        context['countries'] = countries
        context['hotels'] = hotels
        context['reviews'] = reviews
        context['form'] = HotelFilterForm()
        return context
